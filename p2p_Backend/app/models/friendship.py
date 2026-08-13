"""Friendship ORM model — a saved contact, one direction only."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Friendship(Base):
    """One row means "user_id saved friend_id to their list" — and nothing more.

    Deliberately directional: there is no approval step and no implied reverse
    row, so Alice having Bob on her list says nothing about Bob's list. That
    makes this a saved-payees list rather than a social graph, which is what
    the Send Money flow actually needs.
    """

    __tablename__ = "friendships"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    friend_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # The DB-level guarantee behind FriendshipAlreadyExistsError: even if two
    # concurrent requests both pass the service's "already a friend?" check,
    # only one insert can land.
    __table_args__ = (UniqueConstraint("user_id", "friend_id", name="uq_friendship_pair"),)
