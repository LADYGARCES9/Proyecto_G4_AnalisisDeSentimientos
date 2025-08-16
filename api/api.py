# api/app.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
import pandas as pd

# rutas del proyecto
try:
    from src.utils.config_rutas import reports_dir
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
    from utils.config_rutas import reports_dir

# helpers de logging
try:
    from src.utils.loggers import append_result, append_alert
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
    from utils.loggers import append_result, append_alert

app = FastAPI(title="Sentiment API", version="0.2.0")

RESULTS_CSV = reports_dir / "results_log.csv"
ALERTS_CSV  = reports_dir / "alerts_log.csv"
reports_dir.mkdir(parents=True, exist_ok=True)

class BatchReq(BaseModel):
    csv_path: str
    text_col: str
    max_rows: Optional[int] = 1000

class Item(BaseModel):
    text: str

class BatchItems(BaseModel):
    items: List[Item]

@app.get("/health")
def health():
    return {"status": "ok"}

# ===== utilidades simples =====
NEG_KW = {"late","broken","refund","bad","terrible","defect","poor","damaged","slow"}
POS_KW = {"good","great","excellent","perfect","amazing","love","works","nice","fast"}

def simple_sentiment(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in NEG_KW): return "negative"
    if any(k in t for k in POS_KW): return "positive"
    return "neutral"

def simple_urgency(text: str, sentiment: str) -> str:
    t = (text or "").lower()
    if sentiment == "negative" and any(k in t for k in {"broken","refund","late","missing"}):
        return "high"
    return "low"

def infer_aspects(text: str) -> str:
    tags = []
    t = (text or "").lower()
    if "price" in t or "$" in t: tags.append("precio")
    if "quality" in t or "defect" in t or "broken" in t: tags.append("calidad")
    if "shipping" in t or "delivery" in t or "late" in t: tags.append("envío")
    return "|".join(tags)

# ===== endpoints =====
@app.post("/predict")
def predict_one(item: Item):
    try:
        s = simple_sentiment(item.text)
        u = simple_urgency(item.text, s)
        a = infer_aspects(item.text)
        append_result(RESULTS_CSV, item.text, s, u, a)
        if s == "negative" and u == "high":
            append_alert(ALERTS_CSV, "negativo/alto", "negative", "high", "umbral auto", a)
        return {"ok": True, "sentiment": s, "urgency": u, "aspects": a}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"error en /predict: {e}"})

@app.post("/batch")
def batch_csv(req: BatchReq):
    try:
        path = Path(req.csv_path)
        if not path.exists():
            return JSONResponse(status_code=400, content={"detail": f"CSV no existe: {path}"})
        df = pd.read_csv(path)
        cols = [c.strip() for c in df.columns.tolist()]
        if req.text_col not in cols:
            return JSONResponse(status_code=400, content={"detail": f"Columna '{req.text_col}' no está en el CSV", "cols": cols})
        n = min(len(df), req.max_rows or len(df))
        processed = 0
        neg_high = 0
        for _, row in df.head(n).iterrows():
            txt = str(row[req.text_col])
            s = simple_sentiment(txt)
            u = simple_urgency(txt, s)
            a = infer_aspects(txt)
            append_result(RESULTS_CSV, txt, s, u, a)
            if s == "negative" and u == "high":
                append_alert(ALERTS_CSV, "negativo/alto", s, u, "umbral auto", a)
                neg_high += 1
            processed += 1
        return {"ok": True, "processed": processed, "neg_high_alerts": neg_high, "results_csv": str(RESULTS_CSV), "alerts_csv": str(ALERTS_CSV)}
    except UnicodeDecodeError:
        # reintenta con encoding latino
        try:
            df = pd.read_csv(req.csv_path, encoding="latin-1")
            return JSONResponse(status_code=400, content={"detail": "Encoding UTF-8 falló. Vuelve a llamar con latin-1 si es necesario."})
        except Exception as e2:
            return JSONResponse(status_code=500, content={"detail": f"error de encoding: {e2}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"error en /batch: {e}"})

@app.post("/batch-items")
def batch_items(payload: BatchItems):
    try:
        processed = 0
        neg_high = 0
        for it in payload.items:
            txt = it.text
            s = simple_sentiment(txt)
            u = simple_urgency(txt, s)
            a = infer_aspects(txt)
            append_result(RESULTS_CSV, txt, s, u, a)
            if s == "negative" and u == "high":
                append_alert(ALERTS_CSV, "negativo/alto", s, u, "umbral auto", a)
                neg_high += 1
            processed += 1
        return {"ok": True, "processed": processed, "neg_high_alerts": neg_high}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"error en /batch-items: {e}"})
