from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"name": "Data Coyote API", "status": "ok"}

@app.get("/health")
def health():
    return {"ok": True, "message": "pong"}
