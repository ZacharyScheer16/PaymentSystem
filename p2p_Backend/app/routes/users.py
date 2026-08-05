"""User signup endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def sign_up(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> UserRead:
    service = UserService(db)
    user = service.sign_up(payload.username, payload.password)
    return user