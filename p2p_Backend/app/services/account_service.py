"""Business logic for account management."""

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import AccountNotFoundError
from app.models.account import Account


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

    def deposit(self, account_id: uuid.UUID, amount: float) -> Account:
        """Add funds to an account. Admin/testing tool — no real funding source is wired up yet."""
        account = self._db.query(Account).filter(Account.id == account_id).with_for_update().first()
        if not account:
            raise AccountNotFoundError
        account.balance += Decimal(str(amount))
        self._db.commit()
        self._db.refresh(account)
        return account
