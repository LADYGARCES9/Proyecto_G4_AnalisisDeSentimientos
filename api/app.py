# api/app.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from pathlib import Path
import os, json, uuid, threading

# ===== rutas del proyecto =====
try:
    from src.utils.config_rutas import reports_dir
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
    from utils.config_rutas import reports_dir

# ===== helpers de logging (tuyos) =====
try:
    from src.utils.loggers import append_result, append_alert
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
    from utils.loggers import append_result, append_alert

# ===== Kafka =====
from confluent_kafka import Producer, Consumer

# ENV (ajústalas en Railway)
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
TOPIC_SENT_IN  = os.getenv("TOPIC_SENT_IN",  "ml.sentiment.in")
TOPIC_SENT_OUT = os.getenv("TOPIC_SENT_OUT", "ml.sentiment.out")
# (Opcional) ABSA si luego lo usas:
TOPIC_ABSA_IN  = os.getenv("TOPIC_ABSA_IN",  "ml.absa.in")
TOPIC_ABSA_OUT = os.getenv("TOPIC_ABSA_OUT", "ml.absa.out")

GROUP_ID = os.getenv("GROUP_ID", "integration-api-v1")

# ===== App =====
app = FastAPI(title="Sentiment API (Kafka)", version="1.0.0")

RESULTS_CSV = reports_dir / "results_log.csv"
ALERTS_CSV  = reports_dir / "alerts_log.csv"
reports_dir.mkdir(parents=True, exist_ok=True)

# ===== modelos de request =====
class BatchReq(BaseModel):
    csv_path: str
    text_col: str
    max_rows: Optional[int] = 1000

class Item(BaseModel):
    text: str

class BatchItems(BaseModel):
    items: List[Item]

# ===== caches en memoria =====
RESULTS: Dict[str, Dict] = {}      # cid -> evento de salida del worker
PENDING_TEXT: Dict[str, str] = {}  # cid -> texto original (para logging/alertas)

# ===== utilidades =====
NEG_KW = {"late","broken","refund","bad","terrible","defect","poor","damaged","slow","missing"}
POS_KW = {"good","great","excellent","perfect","amazing","love","works","nice","fast"}

def simple_urgency(text: str, sentiment: str) -> str:
    t = (text or "").lower()
    if sentiment == "negative" and any(k in t for k in {"broken","refund","late","missing","defect"}):
        return "high"
    return "low"

def infer_aspects_keywords(text: str) -> str:
    # Solo por si aún no tienes ABSA worker; si lo tienes, usa lo que venga de Kafka
    tags = []
    t = (text or "").lower()
    if "price" in t or "$" in t: tags.append("precio")
    if "quality" in t or "defect" in t or "broken" in t: tags.append("calidad")
    if "shipping" in t or "delivery" in t or "late" in t: tags.append("envío")
    return "|".join(tags)

# ===== Kafka producer =====
producer = Producer({"bootstrap.servers": KAFKA_BROKERS})

def enqueue(topic: str, payload: dict) -> str:
    cid = str(uuid.uuid4())
    evt = {"correlation_id": cid, "payload": payload, "meta": {"source": "integration-api"}}
    producer.produce(topic, json.dumps(evt).encode("utf-8"), key=cid)
    producer.flush()
    return cid

# ===== background consumer (lee *sentiment.out* y (opcional) *absa.out*) =====
def bg_consume():
    cons = Consumer({
        "bootstrap.servers": KAFKA_BROKERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    topics = [TOPIC_SENT_OUT]
    if TOPIC_ABSA_OUT:
        topics.append(TOPIC_ABSA_OUT)
    cons.subscribe(topics)
    print(f"🔊 Listening results on: {', '.join(topics)}")
    try:
        while True:
            msg = cons.poll(1.0)
            if not msg:
                continue
            if msg.error():
                print("KafkaErr:", msg.error())
                continue
            try:
                evt = json.loads(msg.value().decode("utf-8"))
                cid = evt.get("correlation_id")
                if not cid:
                    continue
                RESULTS[cid] = evt

                # —— Logging a CSVs usando tu helper ——
                text = PENDING_TEXT.pop(cid, None)  # recupera el texto original (si lo tenemos)
                if text:
                    # Estructura esperada del worker de Sentiment: {"result": {"prediction": <str>, "proba": [...]}}
                    res = evt.get("result", {})
                    sentiment = str(res.get("prediction", "neutral"))
                    # urgencia basada en texto + sentimiento
                    urg = simple_urgency(text, sentiment)

                    # Si el evento viene del ABSA y trae dict de aspectos, úsalo; si no, usa keywords
                    aspects_val = res if isinstance(res, dict) and "prediction" not in res else infer_aspects_keywords(text)
                    if isinstance(aspects_val, dict):
                        # convierte dict aspectos->label a string "aspecto:label|..."
                        aspects_str = "|".join(f"{k}:{v}" for k, v in aspects_val.items())
                    else:
                        aspects_str = aspects_val

                    append_result(RESULTS_CSV, text, sentiment, urg, aspects_str)
                    if sentiment == "negative" and urg == "high":
                        append_alert(ALERTS_CSV, "negativo/alto", sentiment, urg, "umbral auto", aspects_str)

                print("✅ stored:", cid)
            except Exception as e:
                print("❌ parse error:", e)
    finally:
        cons.close()

@app.on_event("startup")
def _startup():
    t = threading.Thread(target=bg_consume, daemon=True)
    t.start()

# ===== endpoints =====
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict_one(item: Item):
    """
    Encola el texto al tópico de SENTIMENT. Devuelve correlation_id.
    El resultado quedará disponible en /result/{cid} cuando el worker responda.
    """
    try:
        cid = enqueue(TOPIC_SENT_IN, {"text": item.text})
        PENDING_TEXT[cid] = item.text  # guardamos el texto para logging cuando llegue la respuesta
        return {"ok": True, "correlation_id": cid}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"error en /predict: {e}"})

@app.post("/batch")
def batch_csv(req: BatchReq):
    """
    Encola cada fila a SENTIMENT. Devuelve la lista de cids.
    (Los CSVs de resultados/alertas se irán llenando cuando lleguen las respuestas.)
    """
    from pandas import read_csv
    try:
        path = Path(req.csv_path)
        if not path.exists():
            return JSONResponse(status_code=400, content={"detail": f"CSV no existe: {path}"})
        df = read_csv(path)
        cols = [c.strip() for c in df.columns.tolist()]
        if req.text_col not in cols:
            return JSONResponse(status_code=400, content={"detail": f"Columna '{req.text_col}' no está en el CSV", "cols": cols})
        n = min(len(df), req.max_rows or len(df))
        cids = []
        for _, row in df.head(n).iterrows():
            txt = str(row[req.text_col])
            cid = enqueue(TOPIC_SENT_IN, {"text": txt})
            PENDING_TEXT[cid] = txt
            cids.append(cid)
        return {"ok": True, "queued": len(cids), "correlation_ids": cids}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"error en /batch: {e}"})

@app.post("/batch-items")
def batch_items(payload: BatchItems):
    try:
        cids = []
        for it in payload.items:
            txt = it.text
            cid = enqueue(TOPIC_SENT_IN, {"text": txt})
            PENDING_TEXT[cid] = txt
            cids.append(cid)
        return {"ok": True, "queued": len(cids), "correlation_ids": cids}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"error en /batch-items: {e}"})

@app.get("/result/{cid}")
def get_result(cid: str):
    evt = RESULTS.get(cid)
    if not evt:
        raise HTTPException(status_code=404, detail="Result not found yet")
    return evt
