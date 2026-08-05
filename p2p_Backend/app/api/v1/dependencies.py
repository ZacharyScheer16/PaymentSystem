"""FastAPI dependency wiring.

This is the one place that binds abstract repository/service interfaces to
concrete implementations. Routers (upstream) and services (downstream) only
ever see the abstraction — this module is where Dependency Inversion actually
gets wired together at runtime.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.sqlalchemy_account_repository import SqlAlchemyAccountRepository
from app.repositories.sqlalchemy_transaction_repository import SqlAlchemyTransactionRepository
from app.services.account_service import AccountService
from app.services.transfer_service import TransferService


def get_account_repository(db: Annotated[Session, Depends(get_db)]) -> SqlAlchemyAccountRepository:
    return SqlAlchemyAccountRepository(db)


def get_transaction_repository(db: Annotated[Session, Depends(get_db)]) -> SqlAlchemyTransactionRepository:
    return SqlAlchemyTransactionRepository(db)


def get_account_service(
    account_repository: Annotated[SqlAlchemyAccountRepository, Depends(get_account_repository)],
) -> AccountService:
    return AccountService(account_repository)


def get_transfer_service(
    account_repository: Annotated[SqlAlchemyAccountRepository, Depends(get_account_repository)],
    transaction_repository: Annotated[SqlAlchemyTransactionRepository, Depends(get_transaction_repository)],
) -> TransferService:
    return TransferService(account_repository, transaction_repository)
