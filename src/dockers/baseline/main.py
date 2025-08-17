import os, json, time, joblib
from confluent_kafka import Consumer, Producer

# ---- Kafka (PLAINTEXT) ----
BOOTSTRAP = os.getenv("KAFKA_BROKERS", "kafka:9092")
GROUP_ID  = os.getenv("GROUP_ID", "sentiment-consumer")
TOPIC_IN  = os.getenv("TOPIC_IN", "ml.sentiment.in")
TOPIC_OUT = os.getenv("TOPIC_OUT", "ml.sentiment.out")

# ---- Modelo ----
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/02_baseline_best.joblib")
bundle = joblib.load(MODEL_PATH)         # esperado: {"model": clf, "preproc": vectorizer?}
model  = bundle["model"]
pre    = bundle.get("preproc")

def infer(payload: dict | str):
    text = payload["text"] if isinstance(payload, dict) else str(payload)
    X = pre.transform([text]) if pre else [text]
    y = model.predict(X)[0]
    proba = getattr(model, "predict_proba", None)
    return {"prediction": y, "proba": proba(X)[0].tolist() if proba else None}

# ---- Kafka clients ----
c = Consumer({"bootstrap.servers": BOOTSTRAP, "group.id": GROUP_ID,
              "auto.offset.reset": "earliest", "enable.auto.commit": True})
p = Producer({"bootstrap.servers": BOOTSTRAP})

def main():
    c.subscribe([TOPIC_IN])
    print(f"✅ Sentiment listening: {TOPIC_IN}")
    try:
        while True:
            m = c.poll(1.0)
            if not m: continue
            if m.error(): print("KafkaErr:", m.error()); continue
            try:
                evt = json.loads(m.value().decode("utf-8"))
                cid = evt.get("correlation_id", "no-cid")
                res = infer(evt.get("payload", ""))
                out = {"correlation_id": cid, "result": res, "ts": time.time()}
                p.produce(TOPIC_OUT, json.dumps(out).encode("utf-8"), key=cid); p.poll(0)
                print("✅ processed:", out)
            except Exception as e:
                print("❌ processing error:", e)
    finally:
        c.close(); p.flush()

if __name__ == "__main__":
    main()
