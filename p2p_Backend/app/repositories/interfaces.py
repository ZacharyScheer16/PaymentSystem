"""Repository interfaces (abstractions) that the service layer depends on.

Services should only ever import from this module, never a concrete
repository. That's what makes it possible to swap Postgres for something
else, or substitute a fake in-memory repository in unit tests, without
touching business logic — this is the Dependency Inversion Principle in
practice.
"""

import uuid
from abc import ABC, abstractmethod

from app.models.account import Account
from app.models.transaction import LedgerEntry


class AccountRepository(ABC):
    @abstractmethod
    def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        """Fetch a single account, or None if it doesn't exist."""

    @abstractmethod
    def create(self, account: Account) -> Account:
        """Persist a new account."""

    @abstractmethod
    def update_balance(self, account_id: uuid.UUID, new_balance: float) -> None:
        """Persist a new cached balance for an existing account."""


class TransactionRepository(ABC):
    @abstractmethod
    def get_by_transfer_id(self, transfer_id: uuid.UUID) -> list[LedgerEntry]:
        """Fetch all ledger entries belonging to a single transfer."""

    @abstractmethod
    def find_by_idempotency_key(self, idempotency_key: str) -> list[LedgerEntry]:
        """Fetch existing entries for an idempotency key, so a retried transfer isn't double-applied."""

    @abstractmethod
    def add_entries(self, entries: list[LedgerEntry]) -> list[LedgerEntry]:
        """Persist a batch of ledger entries as a single atomic unit (one DB transaction)."""
