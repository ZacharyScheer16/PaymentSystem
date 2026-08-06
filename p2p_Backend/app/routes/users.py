"""User signup and login endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import UserNotFoundError
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.account import AccountRead
from app.schemas.user import AuthResponse, RecipientRead, UserCreate, UserLogin, UserRead
from app.services.account_service import AccountService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


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
