"""User signup, login, and directory-search endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.core.exceptions import UserNotFoundError
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.account import AccountRead
from app.schemas.friend import UserSearchResult
from app.schemas.user import AuthResponse, RecipientRead, UserCreate, UserLogin, UserRead
from app.services.account_service import AccountService
from app.services.friend_service import FriendService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


# Declared before /{username}/recipient so "search" is never read as a username.
@router.get("/search", response_model=list[UserSearchResult])
def search_users(
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
    q: Annotated[str, Query(max_length=50)] = "",
    limit: Annotated[int, Query(ge=1, le=25)] = 10,
) -> list[UserSearchResult]:
    """Typeahead lookup for the Send Money and Add Friend inputs.

    Requires a token: this is the one endpoint that will happily enumerate
    usernames, so it shouldn't be open to anonymous callers. Being
    authenticated also gives us the caller's id for free, which is what lets us
    drop them from their own results and mark who's already a friend.
    """
    user_service = UserService(db)
    friend_service = FriendService(db)

    matches = user_service.search_users(q, exclude_user_id=current_user_id, limit=limit)
    friend_ids = friend_service.get_friend_ids(current_user_id)

    return [
        UserSearchResult(id=user.id, username=user.username, is_friend=user.id in friend_ids)
        for user in matches
    ]


@router.get("/{username}/recipient", response_model=RecipientRead)
def get_recipient(username: str, db: Annotated[Session, Depends(get_db)]) -> RecipientRead:
    """Resolve a username to an account_id — used by the Send Money flow to
    find a transfer target without exposing raw account UUIDs to look up."""
    user_service = UserService(db)
    account_service = AccountService(db)

    user = user_service.get_user_by_username(username)
    if not user:
        raise UserNotFoundError

    account = account_service.get_account_by_owner(user.id)
    return RecipientRead(username=user.username, account_id=account.id)


@router.post("/", response_model=AuthResponse)
def sign_up(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> AuthResponse:
    user_service = UserService(db)
    account_service = AccountService(db)

    # Two services, one workflow: create the identity, then open its first
    # account. Each service still only knows about its own table.
    user = user_service.sign_up(payload.username, payload.password)
    account = account_service.open_account(owner_id=user.id, currency="USD", opening_balance=0)

    return AuthResponse(
        user=UserRead.model_validate(user),
        account=AccountRead.model_validate(account),
        access_token=create_access_token(user.id),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Annotated[Session, Depends(get_db)]) -> AuthResponse:
    user_service = UserService(db)
    account_service = AccountService(db)

    user = user_service.authenticate(payload.username, payload.password)
    account = account_service.get_account_by_owner(user.id)

    return AuthResponse(
        user=UserRead.model_validate(user),
        account=AccountRead.model_validate(account),
        access_token=create_access_token(user.id),
    )
