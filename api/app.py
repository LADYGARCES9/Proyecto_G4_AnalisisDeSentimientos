from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True, "msg": "API up"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test():
    return {"ok": True, "message": "🚀 API funcionando correctamente"}
