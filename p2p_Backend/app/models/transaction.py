"""LedgerEntry ORM model — one row per debit or credit.

A single P2P transfer produces exactly two LedgerEntry rows: a DEBIT on the
sender's account and a CREDIT on the receiver's, sharing one `transfer_id`,
persisted atomically. See services/transfer_service.py for the orchestration.
This replaces the old single-row-per-transaction design in defenseLayer.sql.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EntryType(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        # Same idempotency_key can appear twice (once per entry_type) for the
        # DEBIT+CREDIT pair of a single transfer, but never more than that.
        UniqueConstraint("idempotency_key", "entry_type", name="uq_ledger_entry_idempotency"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transfer_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    entry_type: Mapped[EntryType] = mapped_column(Enum(EntryType), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING
    )
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
