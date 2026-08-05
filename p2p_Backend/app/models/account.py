"""Account ORM model — the owner of a balance in the ledger."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Account(Base):
    """A single account that ledger entries (transactions) are posted against.

    `balance` is a cached value for fast reads. The source of truth is the sum
    of this account's LedgerEntry rows — reconciling the two is a good
    service-layer invariant to assert in tests.
    """

    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_name: Mapped[str] = mapped_column(String(120), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    balance: Mapped[float] = mapped_column(Numeric(precision=18, scale=2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
