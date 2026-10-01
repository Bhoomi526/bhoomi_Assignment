from fastapi import FastAPI

app = FastAPI(
    title="CMPUT 401 Assignment 1 API",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}