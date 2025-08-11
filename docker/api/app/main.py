from fastapi import FastAPI

app = FastAPI(title="ResearchAI API")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
