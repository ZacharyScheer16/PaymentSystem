"""Account endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.db.session import get_db
from app.schemas.account import AccountCreate, AccountDeposit, AccountRead
from app.services.account_service import AccountService
from app.schemas.transaction import LedgerEntryRead
from app.services.transfer_service import TransferService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountRead)
def create_account(payload: AccountCreate, db: Annotated[Session, Depends(get_db)]) -> AccountRead:
    service = AccountService(db)
    account = service.open_account(payload.owner_id, payload.currency, payload.opening_balance)
    return account



@router.get("/{account_id}", response_model=AccountRead)
def get_account(account_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> AccountRead:
    service = AccountService(db)
    account = service.get_account(account_id)
    return account


@router.post("/{account_id}/deposit", response_model=AccountRead)
def deposit(
    account_id: uuid.UUID,
    payload: AccountDeposit,
    db: Annotated[Session, Depends(get_db)],
    current_user_id: Annotated[uuid.UUID, Depends(get_current_user_id)],
) -> AccountRead:
    """Add money to your own account. No real funding source is wired up yet."""
    service = AccountService(db)
    account = service.deposit(
        caller_user_id=current_user_id,
        account_id=account_id,
        amount=payload.amount,
        idempotency_key=payload.idempotency_key,
    )
    return account

@router.get("/{account_id}/transfers", response_model=list[LedgerEntryRead])
def get_account_transfers(account_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> list[LedgerEntryRead]:
    service = TransferService(db)
    entries = service.get_account_entries(account_id)
    return entries
