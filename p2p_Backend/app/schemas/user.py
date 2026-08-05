"""Pydantic DTOs for the User/signup API surface."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.account import AccountRead


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    created_at: datetime


class AuthResponse(BaseModel):
    """What both signup and login return: a user, their account, and a bearer token.

    The frontend should store `access_token` and send it as
    `Authorization: Bearer <access_token>` on every subsequent request.
    """

    user: UserRead
    account: AccountRead
    access_token: str
    token_type: str = "bearer"
