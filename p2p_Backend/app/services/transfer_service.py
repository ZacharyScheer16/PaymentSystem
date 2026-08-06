"""Business logic for P2P transfers — the core of the payments domain."""

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AccountNotFoundError, ForbiddenError, InsufficientFundsError
from app.models.account import Account
from app.models.transaction import EntryType, LedgerEntry, TransactionStatus


class TransferService:
    def __init__(self, db: Session):
        self._db = db

    def get_transfer_entries(self, transfer_id: uuid.UUID) -> list[LedgerEntry]:
        """Fetch all LedgerEntry rows for a given transfer_id."""
        entries = self._db.query(LedgerEntry).filter(LedgerEntry.transfer_id == transfer_id).all()
        return entries
    
    def get_account_entries(self, account_id: uuid.UUID) -> list[LedgerEntry]:
        entries = self._db.query(LedgerEntry).filter(LedgerEntry.account_id 
             == account_id).order_by(LedgerEntry.created_at.desc()).all()
        return entries

    def execute_transfer(
        self,
        caller_user_id: uuid.UUID,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        amount: float,
        idempotency_key: str,
    ) -> uuid.UUID:
        """Move `amount` from sender to receiver as a single atomic operation.

        Both account rows are locked with SELECT ... FOR UPDATE (in a
        consistent id order, to avoid deadlocking against a concurrent
        transfer running in the opposite direction) before the balance check,
        so two transfers racing on the same sender account can't both read
        the same starting balance and overdraw it.
        """
        existing_entry = self._db.query(LedgerEntry).filter(LedgerEntry.idempotency_key == idempotency_key).first()
        if existing_entry:
            return existing_entry.transfer_id

        # Lock both account rows for the duration of this transaction so a
        # concurrent transfer touching either account can't read a stale
        # balance. Always lock in a consistent order (sorted by id) — if two
        # transfers move money in opposite directions between the same pair
        # of accounts, locking sender-then-receiver in each would deadlock.
        locked_accounts = {
            account.id: account
            for account in self._db.query(Account)
            .filter(Account.id.in_([sender_account_id, receiver_account_id]))
            .order_by(Account.id)
            .with_for_update()
            .all()
        }
        senderAccount = locked_accounts.get(sender_account_id)
        receiverAccount = locked_accounts.get(receiver_account_id)
        if not senderAccount or not receiverAccount:
            raise AccountNotFoundError
        if senderAccount.owner_id != caller_user_id:
            raise ForbiddenError
        if amount <= 0 or senderAccount.balance < amount:
            raise InsufficientFundsError

        transfer_id = uuid.uuid4()
        # Account.balance is a Decimal (Numeric column) but `amount` arrives as a
        # float from the API — Decimal refuses to mix with float in arithmetic
        # (that's Python protecting against float rounding errors in money math),
        # so convert once here before doing any balance math.
        amount = Decimal(str(amount))

        debit_entry = LedgerEntry(
            transfer_id=transfer_id,
            account_id=senderAccount.id,
            entry_type=EntryType.DEBIT,
            amount=amount,
            status=TransactionStatus.COMPLETED,
            idempotency_key=idempotency_key,
        )
        credit_entry = LedgerEntry(
            transfer_id=transfer_id,
            account_id=receiverAccount.id,
            entry_type=EntryType.CREDIT,
            amount=amount,
            status=TransactionStatus.COMPLETED,
            idempotency_key=idempotency_key,
        )
        senderAccount.balance -= amount
        receiverAccount.balance += amount

        self._db.add(debit_entry)
        self._db.add(credit_entry)
        self._db.commit()

        return transfer_id