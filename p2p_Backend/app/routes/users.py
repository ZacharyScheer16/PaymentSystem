"""User signup endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.account import AccountRead
from app.schemas.user import SignupResponse, UserCreate, UserRead
from app.services.account_service import AccountService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=SignupResponse)
def sign_up(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> SignupResponse:
    user_service = UserService(db)
    account_service = AccountService(db)

    # Two services, one workflow: create the identity, then open its first
    # account. Each service still only knows about its own table.
    user = user_service.sign_up(payload.username, payload.password)
    account = account_service.open_account(owner_id=user.id, currency="USD", opening_balance=0)

    return SignupResponse(
        user=UserRead.model_validate(user),
        account=AccountRead.model_validate(account),
    )
