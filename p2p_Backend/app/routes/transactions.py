"""Transfer endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transaction import TransferRequest, TransferResponse
from app.services.transfer_service import TransferService

router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.post("/", response_model=TransferResponse)
def create_transfer(payload: TransferRequest, db: Annotated[Session, Depends(get_db)]) -> TransferResponse:
    service = TransferService(db)
    transfer_id = service.execute_transfer(
        sender_account_id=payload.sender_account_id,
        receiver_account_id=payload.receiver_account_id,
        amount=payload.amount,
        idempotency_key=payload.idempotency_key,
    )
    entries = service.get_transfer_entries(transfer_id)
    return TransferResponse(transfer_id=transfer_id, entries=entries)
