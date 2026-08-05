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


class UsernameAlreadyExistsError(DomainError):
    """Raised when signing up with a username that's already taken."""


class InvalidCredentialsError(DomainError):
    """Raised when a login's username doesn't exist or its password doesn't match."""


class InvalidTokenError(DomainError):
    """Raised when a JWT is missing, malformed, expired, or has a bad signature."""


class ForbiddenError(DomainError):
    """Raised when an authenticated user tries to act on an account they don't own."""
