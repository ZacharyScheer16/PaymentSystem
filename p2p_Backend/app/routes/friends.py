"""Friends-list endpoints.

Every route here takes the acting user from the bearer token, never from the
path or body — so there is no shape of request that edits someone else's list.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.db.session import get_db
from app.schemas.friend import FriendCreate, FriendRead
from app.services.friend_service import FriendService

router = APIRouter(prefix="/friends", tags=["friends"])


@router.get("/", response_model=list[FriendRead])
def list_friends(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> list[FriendRead]:
    service = FriendService(db)
    return service.list_friends(current_user_id)


@router.post("/", response_model=FriendRead)
def add_friend(
    payload: FriendCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> FriendRead:
    service = FriendService(db)
    return service.add_friend(current_user_id, payload.username)


@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_friend(
    friend_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> None:
    service = FriendService(db)
    service.remove_friend(current_user_id, friend_id)
