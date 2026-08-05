"""Transfer endpoints — thin: validate input via schemas, delegate to TransferService, return a schema."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_transfer_service
from app.schemas.transaction import TransferRequest, TransferResponse
from app.services.transfer_service import TransferService

router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.post("/", response_model=TransferResponse)
def create_transfer(
    payload: TransferRequest,
    transfer_service: Annotated[TransferService, Depends(get_transfer_service)],
) -> TransferResponse:
    # TODO: call transfer_service.execute_transfer(...) to get a transfer_id,
    # then look up the resulting entries (e.g. via the transaction repository
    # or a method you add to TransferService) and return them.
    raise NotImplementedError
