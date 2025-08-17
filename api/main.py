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

# ===== helpers de logging =====
try:
    from src.utils.loggers import append_result, append_alert
except ModuleNotFoundError:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
    from utils.loggers import append_result, append_alert

# ===== Kafka =====
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
TOPIC_SENT_IN  = os.getenv("TOPIC_SENT_IN",  "ml.sentiment.in")
TOPIC_SENT_OUT = os.getenv("TOPIC_SENT_OUT", "ml.sentiment.out")
TOPIC_ABSA_IN  = os.getenv("TOPIC_ABSA_IN",  "ml.absa.in")
TOPIC_ABSA_OUT = os.getenv("TOPIC_ABSA_OUT", "ml.absa.out")
GROUP_ID = os.getenv("GROUP_ID", "integration-api-v1")

# ===== App =====
app = FastAPI(title="Sentiment API (Kafka)", version="1.0.0")

RESULTS_CSV = reports_dir / "results_log.csv"
ALERTS_CSV  = reports_dir / "alerts_log.csv"
reports_dir.mkdir(parents=True, exist_ok=True)

# ===== modelos =====
class BatchReq(BaseModel):
    csv_path: str
    text_col: str
    max_rows: Optional[int] = 1000

class Item(BaseModel):
    text: str

class BatchItems(BaseModel):
    items: List[Item]

# ===== caches =====
RESULTS: Dict[str, Dict] = {}
PENDING_TEXT: Dict[str, str] = {}

# ===== helpers =====
def simple_urgency(text: str, sentiment: str) -> str:
    t = (text or "").lower()
    if sentiment == "negative" and any(k in t for k in {"broken","refund","late","missing","defect"}):
        return "high"
    return "low"

def infer_aspects_keywords(text: str) -> str:
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

# ===== asegurador de tópicos =====
def ensure_topics(bootstrap: str, topics: List[str]):
    admin = AdminClient({"bootstrap.servers": bootstrap})
    md = admin.list_topics(timeout=5)
    missing = [t for t in topics if t not in md.topics]
    if not missing:
        print("✅ Topics ya existen:", ", ".join(topics))
        return
    new = [NewTopic(t, num_partitions=1, replication_factor=1) for t in missing]
    fs = admin.create_topics(new)
    for t, f in fs.items():
        try:
            f.result()
            print(f"🆕 Topic creado: {t}")
        except Exception as e:
            print(f"⚠️ No se pudo crear {t}: {e}")

# ===== consumer en background =====
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
            if not msg: continue
            if msg.error():
                print("KafkaErr:", msg.error()); continue
            try:
                evt = json.loads(msg.value().decode("utf-8"))
                cid = evt.get("correlation_id")
                if not cid: continue
                RESULTS[cid] = evt

                text = PENDING_TEXT.pop(cid, None)
                if text:
                    res = evt.get("result", {})
                    sentiment = str(res.get("prediction", "neutral"))
                    urg = simple_urgency(text, sentiment)

                    aspects_val = res if isinstance(res, dict) and "prediction" not in res else infer_aspects_keywords(text)
                    aspects_str = "|".join(f"{k}:{v}" for k, v in aspects_val.items()) if isinstance(aspects_val, dict) else aspects_val

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
    # crea los topics antes de arrancar el consumer
    ensure_topics(KAFKA_BROKERS, [
        TOPIC_SENT_IN, TOPIC_SENT_OUT,
        TOPIC_ABSA_IN, TOPIC_ABSA_OUT
    ])
    t = threading.Thread(target=bg_consume, daemon=True)
    t.start()

# ===== endpoints =====
@app.post("/test")
def test():
    return {"ok": True, "message": "🚀 API funcionando correctamente"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict_one(item: Item):
    try:
        cid = enqueue(TOPIC_SENT_IN, {"text": item.text})
        PENDING_TEXT[cid] = item.text
        return {"ok": True, "correlation_id": cid, "text": item.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"error en /predict: {e}"})

@app.get("/result/{cid}")
def get_result(cid: str):
    evt = RESULTS.get(cid)
    if not evt:
        raise HTTPException(status_code=404, detail="Result not found yet")
    return evt

# ===== arranque rápido =====
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
