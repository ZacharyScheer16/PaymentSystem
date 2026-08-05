"""Account endpoints — thin: validate input via schemas, delegate to AccountService, return a schema."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_account_service
from app.schemas.account import AccountCreate, AccountRead
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountRead)
def create_account(
    payload: AccountCreate,
    account_service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    # TODO: call account_service.open_account(...) and return the result
    raise NotImplementedError


@router.get("/{account_id}", response_model=AccountRead)
def get_account(
    account_id: uuid.UUID,
    account_service: Annotated[AccountService, Depends(get_account_service)],
) -> AccountRead:
    # TODO: call account_service.get_account(account_id) and return it.
    # Consider: where should AccountNotFoundError become an HTTP 404?
    raise NotImplementedError
