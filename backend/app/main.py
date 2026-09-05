from fastapi import FastAPI

app = FastAPI(title="YATRA-SAARTHI API")


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1"}