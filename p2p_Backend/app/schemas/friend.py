"""Pydantic DTOs for the friends list and the user typeahead."""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class FriendCreate(BaseModel):
    """Add by username — the id the client saw in search results is never
    trusted as the thing to write."""

    username: str = Field(min_length=1, max_length=50)


class FriendRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str


class UserSearchResult(BaseModel):
    """One row of the typeahead dropdown.

    Note what's absent: no account_id. The Send Money flow still resolves that
    through GET /users/{username}/recipient at submit time, so search stays a
    read of public-ish identity and nothing more.
    """

    id: uuid.UUID
    username: str
    is_friend: bool
