# --- carga robusta de artefacto ---
import os, json, time, joblib, glob, re
from sklearn.pipeline import Pipeline
from confluent_kafka import Consumer, Producer


BOOT = os.getenv("KAFKA_BROKERS", "kafka:9092")
TIN  = os.getenv("TOPIC_IN",  "ml..in")
TOUT = os.getenv("TOPIC_OUT", "ml.sentiment.out")
GID  = os.getenv("GROUP_ID",  "sentiment-v1")
MODEL_PATH = os.getenv("MODEL_PATH", "/models/02_baseline_best.joblib")

print(f"🔍 Cargando modelo: {MODEL_PATH}")
obj = joblib.load(MODEL_PATH)

if isinstance(obj, Pipeline):
    pipe = obj
    def infer(payload):
        text = payload["text"] if isinstance(payload, dict) else str(payload)
        y = pipe.predict([text])[0]
        proba = getattr(pipe, "predict_proba", None)
        return {"prediction": y, "proba": proba([text])[0].tolist() if proba else None}
else:
    bundle = obj if isinstance(obj, dict) else {"model": obj}
    model = bundle.get("model") or bundle
    pre   = bundle.get("preproc")
    def infer(payload):
        text = payload["text"] if isinstance(payload, dict) else str(payload)
        X = pre.transform([text]) if pre else [text]
        y = model.predict(X)[0]
        proba = getattr(model, "predict_proba", None)
        return {"prediction": y, "proba": proba(X)[0].tolist() if proba else None}

c = Consumer({"bootstrap.servers": BOOT, "group.id": GID, "auto.offset.reset":"earliest", "enable.auto.commit": True})
p = Producer({"bootstrap.servers": BOOT})

def main():
    c.subscribe([TIN]); print(f"✅ Sentiment listening: {TIN}")
    try:
        while True:
            m = c.poll(1.0)
            if not m: continue
            if m.error(): print("KafkaErr:", m.error()); continue
            evt = json.loads(m.value().decode("utf-8"))
            cid = evt.get("correlation_id","no-cid")
            out = {"correlation_id": cid, "result": infer(evt.get("payload","")), "ts": time.time()}
            p.produce(TOUT, json.dumps(out).encode("utf-8"), key=cid); p.poll(0)
            print("✅ processed:", out)
    finally:
        c.close(); p.flush()

if __name__ == "__main__":
    main()
