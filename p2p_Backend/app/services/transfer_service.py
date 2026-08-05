"""Business logic for P2P transfers — the core of the payments domain."""

import uuid

from sqlalchemy.orm import Session


class TransferService:
    def __init__(self, db: Session):
        self._db = db

    def execute_transfer(
        self,
        sender_account_id: uuid.UUID,
        receiver_account_id: uuid.UUID,
        amount: float,
        idempotency_key: str,
    ) -> uuid.UUID:
        """Move `amount` from sender to receiver as a single atomic operation.

        Suggested algorithm (fill in as you implement):
          1. Check `idempotency_key` — if a LedgerEntry already exists with it,
             return that transfer_id instead of double-applying the transfer.
          2. Load both accounts; raise AccountNotFoundError if either is missing.
          3. Validate amount > 0 and sender.balance >= amount; raise
             InsufficientFundsError otherwise.
          4. Generate a new transfer_id (uuid.uuid4()) shared by both entries.
          5. Create a DEBIT LedgerEntry for the sender and a CREDIT LedgerEntry
             for the receiver, update both account balances.
          6. Commit — both entries and both balance updates succeed together,
             or (on error) neither does.
          7. Return the transfer_id.

        Once this works for one request at a time, the interesting problem
        starts: what happens if two transfers touching the SAME sender
        account arrive at once? Both could read the same starting balance,
        both pass the funds check, both deduct — overdrawing the account.
        That's a race condition. We'll tackle it deliberately once the happy
        path is solid (the usual fix is locking the account row for the
        duration of the transfer).
        """
        raise NotImplementedError
