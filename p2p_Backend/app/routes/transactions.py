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
    # TODO: call service.execute_transfer(...), then look up + return the resulting entries
    raise NotImplementedError
