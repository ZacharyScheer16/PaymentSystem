"""Business logic for account management."""

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AccountNotFoundError, ForbiddenError
from app.models.account import Account
from app.models.transaction import EntryType, LedgerEntry, TransactionStatus


class AccountService:
    def __init__(self, db: Session):
        self._db = db

    def open_account(self, owner_id: uuid.UUID, currency: str, opening_balance: float) -> Account:
        """Create and persist a new account."""
        account = Account(owner_id=owner_id, currency=currency, balance=opening_balance)
        self._db.add(account)
        self._db.commit()
        self._db.refresh(account)
        return account

    def get_account(self, account_id: uuid.UUID) -> Account:
        """Fetch an account by id."""
        account = self._db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise AccountNotFoundError
        return account

    def get_account_by_owner(self, owner_id: uuid.UUID) -> Account:
        """Fetch the account belonging to a given user."""
        account = self._db.query(Account).filter(Account.owner_id == owner_id).first()
        if not account:
            raise AccountNotFoundError
        return account

    def deposit(
        self,
        caller_user_id: uuid.UUID,
        account_id: uuid.UUID,
        amount: float,
        idempotency_key: str,
    ) -> Account:
        """Add funds to the caller's own account, recording a CREDIT ledger entry.

        There's no real funding source wired up yet — the money appears out of
        thin air — but the balance change is still logged to the ledger so every
        movement on an account has a row behind it.

        The account row is locked with SELECT ... FOR UPDATE *before* the
        idempotency check, so two concurrent retries of the same deposit
        serialize: the second one waits, then sees the first one's entry and
        returns without crediting the balance a second time.
        """
        account = self._db.query(Account).filter(Account.id == account_id).with_for_update().first()
        if not account:
            raise AccountNotFoundError
        if account.owner_id != caller_user_id:
            raise ForbiddenError

        existing_entry = (
            self._db.query(LedgerEntry)
            .filter(
                LedgerEntry.idempotency_key == idempotency_key,
                LedgerEntry.account_id == account.id,
            )
            .first()
        )
        if existing_entry:
            return account

        # Account.balance is a Decimal (Numeric column) but `amount` arrives as
        # a float from the API, and Decimal refuses to mix with float in
        # arithmetic — convert once here before touching the balance.
        amount = Decimal(str(amount))
        # A deposit has no counterparty, so unlike a transfer it produces a
        # single CREDIT entry rather than a DEBIT/CREDIT pair. It still gets its
        # own transfer_id so the ledger stays uniformly grouped by that column.
        entry = LedgerEntry(
            transfer_id=uuid.uuid4(),
            account_id=account.id,
            entry_type=EntryType.CREDIT,
            amount=amount,
            status=TransactionStatus.COMPLETED,
            idempotency_key=idempotency_key,
        )
        account.balance += amount

        self._db.add(entry)
        self._db.commit()
        self._db.refresh(account)
        return account
