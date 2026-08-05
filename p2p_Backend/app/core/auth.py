"""FastAPI dependency for reading the current user off a request's JWT.

Kept separate from security.py: that file is pure crypto with no FastAPI
knowledge; this file is the glue that plugs it into a request.
"""

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token

# Expects an `Authorization: Bearer <token>` header. If it's missing entirely,
# FastAPI/Starlette's HTTPBearer raises its own 403 before our code even
# runs — a well-known FastAPI quirk (401 would arguably be more correct for
# "not authenticated at all", but that's the library's default behavior).
_bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> uuid.UUID:
    """Verify the request's bearer token and return the user_id it was issued for."""
    return decode_access_token(credentials.credentials)
