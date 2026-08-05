"""FastAPI application entrypoint. Only app instantiation, middleware, and router mounting — no business logic."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import accounts, transactions
from app.core.config import settings

app = FastAPI(title="PaymentProject API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "PaymentProject backend is running"}
