"""Business logic for account management. No SQL, no FastAPI — only rules."""

import uuid

from app.models.account import Account
from app.repositories.interfaces import AccountRepository


class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self._account_repository = account_repository

    def open_account(self, owner_name: str, currency: str, opening_balance: float) -> Account:
        """Create a new account.

        TODO: decide + enforce any opening-balance rules (e.g. must be >= 0,
        which schemas/account.py already validates at the API boundary —
        should the service re-validate, or trust the caller?).
        """
        raise NotImplementedError

    def get_account(self, account_id: uuid.UUID) -> Account:
        """Fetch an account.

        TODO: raise app.core.exceptions.AccountNotFoundError if it doesn't exist.
        """
        raise NotImplementedError
