# --- carga robusta de artefacto ---
import joblib
from sklearn.pipeline import Pipeline

obj = joblib.load(MODEL_PATH,"src/02_baseline_best.joblib")

# Caso A: guardaste un Pipeline entero (.predict ya maneja el preproc)
if isinstance(obj, Pipeline):
    pipeline = obj
    model = None
    pre = None

    def infer(payload):
        text = payload["text"] if isinstance(payload, dict) else str(payload)
        y = pipeline.predict([text])[0]
        proba_fn = getattr(pipeline, "predict_proba", None)
        out = {"prediction": y}
        if proba_fn:
            out["proba"] = proba_fn([text])[0].tolist()
        return out

# Caso B: guardaste un dict {"model": clf, "preproc": vectorizer}
else:
    bundle = obj
    model = bundle.get("model") or bundle.get("clf") or bundle  # por si es solo el modelo
    pre = bundle.get("preproc")

    def infer(payload):
        text = payload["text"] if isinstance(payload, dict) else str(payload)
        X = pre.transform([text]) if pre else [text]
        y = model.predict(X)[0]
        proba_fn = getattr(model, "predict_proba", None)
        out = {"prediction": y}
        if proba_fn:
            out["proba"] = proba_fn(X)[0].tolist()
        return out


