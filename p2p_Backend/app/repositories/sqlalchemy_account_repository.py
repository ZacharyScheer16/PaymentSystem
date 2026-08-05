"""SQLAlchemy implementation of AccountRepository."""

import uuid

from sqlalchemy.orm import Session

from app.models.account import Account
from app.repositories.interfaces import AccountRepository


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_id(self, account_id: uuid.UUID) -> Account | None:
        raise NotImplementedError

    def create(self, account: Account) -> Account:
        raise NotImplementedError

    def update_balance(self, account_id: uuid.UUID, new_balance: float) -> None:
        raise NotImplementedError
