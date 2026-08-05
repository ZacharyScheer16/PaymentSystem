"""Pydantic DTOs for the User/signup API surface."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.account import AccountRead


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    created_at: datetime


class SignupResponse(BaseModel):
    """What POST /api/users/ returns: the new user AND the account opened for them."""

    user: UserRead
    account: AccountRead
