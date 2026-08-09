"""Pydantic DTOs for the Account API surface — decoupled from app/models/account.py."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    owner_id: uuid.UUID
    currency: str = "USD"
    opening_balance: float = Field(default=0, ge=0)


class AccountDeposit(BaseModel):
    amount: float = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=255)


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    currency: str
    balance: float
    created_at: datetime
