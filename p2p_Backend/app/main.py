"""FastAPI application entrypoint."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import (
    AccountNotFoundError,
    DomainError,
    DuplicateTransferError,
    ForbiddenError,
    InsufficientFundsError,
    InvalidCredentialsError,
    InvalidTokenError,
    UsernameAlreadyExistsError,
)
from app.core.logging import setup_logging
from app.db.base import Base
from app.db.session import engine
from app.models import account, transaction, user  # noqa: F401 — import registers tables on Base.metadata
from app.routes import accounts, transactions, users

# One HTTP status per domain error. DomainError subclasses not listed here
# fall back to 400 — see handle_domain_error below.
_STATUS_BY_EXCEPTION = {
    AccountNotFoundError: 404,
    UsernameAlreadyExistsError: 409,
    DuplicateTransferError: 409,
    InsufficientFundsError: 400,
    InvalidCredentialsError: 401,
    InvalidTokenError: 401,
    ForbiddenError: 403,
}

setup_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready (%s)", settings.database_url)
    yield


app = FastAPI(title="PaymentProject API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    """Translate any domain exception into a clean HTTP error instead of a raw 500.

    Catches DomainError AND every subclass of it (AccountNotFoundError,
    InsufficientFundsError, etc.) — Starlette matches exception handlers by
    walking the class hierarchy, so one handler here covers all of them.
    """
    status_code = _STATUS_BY_EXCEPTION.get(type(exc), 400)
    detail = str(exc) or exc.__class__.__doc__ or exc.__class__.__name__
    return JSONResponse(status_code=status_code, content={"detail": detail})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.1fms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


app.include_router(users.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "PaymentProject backend is running"}
