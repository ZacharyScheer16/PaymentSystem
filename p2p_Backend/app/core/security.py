"""Password hashing and JWT access tokens. Pure crypto — no FastAPI here."""

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import InvalidTokenError


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(user_id: uuid.UUID) -> str:
    """Issue a signed token proving `user_id` logged in, valid for a limited time.

    `sub` (subject) is the standard JWT claim name for "who this token is
    about" — using the real convention here rather than inventing our own.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> uuid.UUID:
    """Verify a token's signature and expiry, returning the user_id it was issued for.

    Raises our own InvalidTokenError (not PyJWT's exceptions) so callers only
    ever need to know about our domain exceptions, not this library's.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise InvalidTokenError from exc
    return uuid.UUID(payload["sub"])
