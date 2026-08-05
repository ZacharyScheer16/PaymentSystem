"""Domain-level exceptions for the payments backend.

Kept separate from FastAPI's HTTPException so services/repositories stay
framework-agnostic. The API layer (routes/) is responsible for translating a
domain exception into the right HTTP status code.
"""


class DomainError(Exception):
    """Base class for all domain-level errors."""


class AccountNotFoundError(DomainError):
    """Raised when an operation references an account that doesn't exist."""


class InsufficientFundsError(DomainError):
    """Raised when a transfer would take the sender's balance below zero."""


class DuplicateTransferError(DomainError):
    """Raised when a transfer is retried with an idempotency key that was already processed."""
