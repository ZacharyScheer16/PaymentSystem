from fastapi import FastAPI

app = FastAPI(title="PaymentProject API", version="1.0.0")


@app.get("/")
def read_root():
    return {"message": "PaymentProject backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
