"""Business logic for P2P transfers — the core of the payments domain.

TransferService is the only place that is allowed to know that a "transfer"
is implemented as two linked LedgerEntry rows. Routers and repositories don't
need to know that.
"""

import uuid

from app.repositories.interfaces import AccountRepository, TransactionRepository


class TransferService:
    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
    ):
        self._account_repository = account_repository
        self._transaction_repository = transaction_repository

    def execute_transfer(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        amount: float,
        idempotency_key: str,
    ) -> uuid.UUID:
        """Move `amount` from sender to receiver as a single atomic operation.

        Suggested algorithm (fill in as you implement):
          1. Check `idempotency_key` via transaction_repository.find_by_idempotency_key()
             — if entries already exist for it, return the existing transfer_id
             instead of double-applying the transfer.
          2. Load both accounts via account_repository.get_by_id(); raise
             AccountNotFoundError if either is missing.
          3. Validate amount > 0 (schemas/transaction.py already checks this at
             the API boundary, but don't trust callers who bypass the API) and
             sender.balance >= amount; raise InsufficientFundsError otherwise.
          4. Generate a new transfer_id (uuid.uuid4()) shared by both entries.
          5. Build a DEBIT LedgerEntry for the sender and a CREDIT LedgerEntry
             for the receiver, both tagged with transfer_id and idempotency_key.
          6. Persist both entries + updated balances atomically via
             transaction_repository.add_entries() — either both succeed or
             neither does. (This is the atomicity guarantee a real ledger needs.)
          7. Return the transfer_id.
        """
        raise NotImplementedError
