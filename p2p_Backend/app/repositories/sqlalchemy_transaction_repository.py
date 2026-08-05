"""SQLAlchemy implementation of TransactionRepository."""

import uuid

from sqlalchemy.orm import Session

from app.models.transaction import LedgerEntry
from app.repositories.interfaces import TransactionRepository


class SqlAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, db: Session):
        self._db = db

    def get_by_transfer_id(self, transfer_id: uuid.UUID) -> list[LedgerEntry]:
        raise NotImplementedError

    def find_by_idempotency_key(self, idempotency_key: str) -> list[LedgerEntry]:
        raise NotImplementedError

    def add_entries(self, entries: list[LedgerEntry]) -> list[LedgerEntry]:
        raise NotImplementedError
