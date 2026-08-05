"""Unit tests for TransferService — run entirely in-memory, no database required.

This is the payoff of depending on AccountRepository/TransactionRepository
abstractions (DIP) instead of SQLAlchemy directly: TransferService can be
tested against the fakes below, in milliseconds, with no Postgres running.
"""

import uuid

import pytest

from app.models.account import Account
from app.models.transaction import LedgerEntry
from app.repositories.interfaces import AccountRepository, TransactionRepository
from app.services.transfer_service import TransferService


class FakeAccountRepository(AccountRepository):
    """In-memory stand-in for SqlAlchemyAccountRepository."""

    def __init__(self, accounts: list[Account] | None = None):
        self._accounts: dict[uuid.UUID, Account] = {a.id: a for a in (accounts or [])}

    def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        return self._accounts.get(account_id)

    def create(self, account: Account) -> Account:
        self._accounts[account.id] = account
        return account

    def update_balance(self, account_id: uuid.UUID, new_balance: float) -> None:
        self._accounts[account_id].balance = new_balance


class FakeTransactionRepository(TransactionRepository):
    """In-memory stand-in for SqlAlchemyTransactionRepository."""

    def __init__(self):
        self._entries: list[LedgerEntry] = []

    def get_by_transfer_id(self, transfer_id: uuid.UUID) -> list[LedgerEntry]:
        return [e for e in self._entries if e.transfer_id == transfer_id]

    def find_by_idempotency_key(self, idempotency_key: str) -> list[LedgerEntry]:
        return [e for e in self._entries if e.idempotency_key == idempotency_key]

    def add_entries(self, entries: list[LedgerEntry]) -> list[LedgerEntry]:
        self._entries.extend(entries)
        return entries


@pytest.fixture
def sender() -> Account:
    return Account(id=uuid.uuid4(), owner_name="Alice", currency="USD", balance=100)


@pytest.fixture
def receiver() -> Account:
    return Account(id=uuid.uuid4(), owner_name="Bob", currency="USD", balance=0)


@pytest.fixture
def transfer_service(sender: Account, receiver: Account) -> TransferService:
    account_repository = FakeAccountRepository([sender, receiver])
    transaction_repository = FakeTransactionRepository()
    return TransferService(account_repository, transaction_repository)


def test_transfer_moves_funds_between_accounts(
    transfer_service: TransferService, sender: Account, receiver: Account
) -> None:
    """A valid transfer should debit the sender and credit the receiver by the same amount."""
    # TODO: call transfer_service.execute_transfer(sender.id, receiver.id, 40, "key-1")
    # then assert sender.balance == 60 and receiver.balance == 40.


def test_transfer_fails_when_sender_has_insufficient_funds(
    transfer_service: TransferService, sender: Account, receiver: Account
) -> None:
    """Should raise InsufficientFundsError and leave both balances unchanged."""
    # TODO: assert app.core.exceptions.InsufficientFundsError is raised when
    # amount > sender.balance, and that neither balance changed.


def test_transfer_is_idempotent(
    transfer_service: TransferService, sender: Account, receiver: Account
) -> None:
    """Retrying the same idempotency_key should not double-apply the transfer."""
    # TODO: call execute_transfer twice with the same idempotency_key and
    # assert the balances only moved once.
