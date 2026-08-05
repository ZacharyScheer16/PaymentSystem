"""Integration tests that hit the real FastAPI app + a test database.

TODO: wire up a test database (e.g. SQLite for speed, or a throwaway Postgres
schema for parity with prod) and override the get_db dependency with a
transactional session that rolls back after each test.
"""


def test_create_transfer_end_to_end() -> None:
    """POST /api/v1/transfers/ with two real accounts should return 200 and matching ledger entries."""
    # TODO
