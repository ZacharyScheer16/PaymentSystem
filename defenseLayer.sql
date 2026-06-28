ALTER TABLE Transactions
ADD CONSTRAINT check_transaction_type
CHECK (TransactionType IN ('CREDIT', 'DEBIT'));