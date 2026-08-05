"""Pydantic DTOs for the Account API surface — decoupled from app/models/account.py."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    owner_id: uuid.UUID
    currency: str = "USD"
    opening_balance: float = Field(default=0, ge=0)


class AccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    currency: str
    balance: float
    created_at: datetime
