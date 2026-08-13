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
# FastAPI/Starlette's HTTPBearer raises 401 before our code even runs. (Older
# FastAPI returned 403 here — a long-standing quirk since corrected upstream —
# so anything asserting 403 on a missing header is out of date.)
_bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer_scheme)],
) -> uuid.UUID:
    """Verify the request's bearer token and return the user_id it was issued for."""
    return decode_access_token(credentials.credentials)
