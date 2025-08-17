import os, json, time, joblib, glob, re
from confluent_kafka import Consumer, Producer

# ---- Kafka ----
BOOTSTRAP = os.getenv("KAFKA_BROKERS", "kafka:9092")
GROUP_ID  = os.getenv("GROUP_ID", "absa-consumer")
TOPIC_IN  = os.getenv("TOPIC_IN", "ml.absa.in")
TOPIC_OUT = os.getenv("TOPIC_OUT", "ml.absa.out")
MODELS_DIR= os.getenv("MODELS_DIR", "/app/models")

# ---- Cargar todos los modelos 04_aspect_*_clf.joblib ----
ASPECT_MODELS = {}  # {"battery": (model, preproc), ...}
paths = sorted(glob.glob(os.path.join(MODELS_DIR, "04_aspect_*_clf.joblib")))
if not paths:
    raise RuntimeError(f"No hay modelos de aspecto en {MODELS_DIR}/04_aspect_*_clf.joblib")

for path in paths:
    bundle = joblib.load(path)              # esperado: {"model": clf, "preproc": vectorizer?}
    model = bundle["model"]; pre = bundle.get("preproc")
    aspect = re.sub(r"^04_aspect_|_clf\.joblib$", "", os.path.basename(path))
    ASPECT_MODELS[aspect] = (model, pre)

print("✅ ABSA loaded aspects:", ", ".join(sorted(ASPECT_MODELS.keys())))

def infer_all(payload: dict | str):
    text = payload["text"] if isinstance(payload, dict) else str(payload)
    results = {}
    for aspect, (model, pre) in ASPECT_MODELS.items():
        X = pre.transform([text]) if pre else [text]
        y = model.predict(X)[0]
        results[aspect] = y
    return results

# ---- Kafka clients ----
c = Consumer({"bootstrap.servers": BOOTSTRAP, "group.id": GROUP_ID,
              "auto.offset.reset":"earliest", "enable.auto.commit": True})
p = Producer({"bootstrap.servers": BOOTSTRAP})

def main():
    c.subscribe([TOPIC_IN])
    print(f"🎧 ABSA listening: {TOPIC_IN}")
    try:
        while True:
            m = c.poll(1.0)
            if not m: continue
            if m.error(): print("KafkaErr:", m.error()); continue
            try:
                evt = json.loads(m.value().decode("utf-8"))
                cid = evt.get("correlation_id","no-cid")
                res = infer_all(evt.get("payload",""))
                out = {"correlation_id": cid, "result": res, "ts": time.time()}
                p.produce(TOPIC_OUT, json.dumps(out).encode("utf-8"), key=cid); p.poll(0)
                print("✅ processed:", out)
            except Exception as e:
                print("❌ processing error:", e)
    finally:
        c.close(); p.flush()

if __name__ == "__main__":
    main()
