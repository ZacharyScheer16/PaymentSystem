"""User signup and login endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.account import AccountRead
from app.schemas.user import AuthResponse, UserCreate, UserLogin, UserRead
from app.services.account_service import AccountService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


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
    )
