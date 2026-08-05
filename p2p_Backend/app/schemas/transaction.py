"""Pydantic DTOs for the transfer/ledger API surface — decoupled from app/models/transaction.py."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import EntryType, TransactionStatus


class TransferRequest(BaseModel):
    sender_account_id: uuid.UUID
    receiver_account_id: uuid.UUID
    amount: float = Field(gt=0)
    idempotency_key: str


class LedgerEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    transfer_id: uuid.UUID
    account_id: uuid.UUID
    entry_type: EntryType
    amount: float
    status: TransactionStatus
    created_at: datetime


class TransferResponse(BaseModel):
    transfer_id: uuid.UUID
    entries: list[LedgerEntryRead]
