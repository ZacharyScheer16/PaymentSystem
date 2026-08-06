"""Manual concurrency tests for TransferService's row-locking.

Fires real concurrent HTTP requests at a running server (not direct service
calls) so the tests exercise actual overlapping DB transactions. Requires the
app to be running against MySQL (uvicorn app.main:app --reload) — under
SQLite these tests are meaningless since SQLite serializes writes at the
whole-file level regardless of our locking code.

Usage:
    venv/Scripts/python.exe scripts/concurrency_test.py
"""

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

BASE_URL = "http://127.0.0.1:8000/api"
TIMEOUT = 10.0


def sign_up(client: httpx.Client, username: str) -> dict:
    response = client.post(f"{BASE_URL}/users/", json={"username": username, "password": "testpass123"})
    response.raise_for_status()
    return response.json()


def deposit(client: httpx.Client, account_id: str, amount: float) -> dict:
    response = client.post(f"{BASE_URL}/accounts/{account_id}/deposit", json={"amount": amount})
    response.raise_for_status()
    return response.json()


def get_account(client: httpx.Client, account_id: str) -> dict:
    response = client.get(f"{BASE_URL}/accounts/{account_id}")
    response.raise_for_status()
    return response.json()


def transfer(client: httpx.Client, token: str, sender_id: str, receiver_id: str, amount: float) -> httpx.Response:
    return client.post(
        f"{BASE_URL}/transfers/",
        json={
            "sender_account_id": sender_id,
            "receiver_account_id": receiver_id,
            "amount": amount,
            "idempotency_key": str(uuid.uuid4()),
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def test_overdraft_race(client: httpx.Client) -> None:
    """20 concurrent $10 transfers out of a $100 account. Exactly 10 should
    succeed and 10 should fail with InsufficientFundsError — if the lock is
    broken, more than 10 will succeed and the account will go negative."""
    print("\n=== Overdraft race test ===")

    unique = uuid.uuid4().hex[:8]
    alice = sign_up(client, f"alice_{unique}")
    bob = sign_up(client, f"bob_{unique}")
    deposit(client, alice["account"]["id"], 100)

    successes = 0
    failures = 0
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = [
            pool.submit(
                transfer, client, alice["access_token"], alice["account"]["id"], bob["account"]["id"], 10
            )
            for _ in range(20)
        ]
        for future in as_completed(futures):
            response = future.result()
            if response.status_code == 200:
                successes += 1
            else:
                failures += 1

    alice_final = get_account(client, alice["account"]["id"])
    bob_final = get_account(client, bob["account"]["id"])

    print(f"Successes: {successes}, Failures: {failures}")
    print(f"Alice final balance: {alice_final['balance']}")
    print(f"Bob final balance:   {bob_final['balance']}")

    assert successes == 10, f"Expected exactly 10 successful transfers, got {successes}"
    assert float(alice_final["balance"]) == 0, f"Alice should be at exactly 0, got {alice_final['balance']}"
    assert float(alice_final["balance"]) >= 0, "Alice's balance went negative — the lock did not hold!"
    print("PASS — no overdraft, exactly 10/20 transfers succeeded.")


def test_deadlock_avoidance(client: httpx.Client) -> None:
    """Opposite-direction transfers between the same two accounts, fired
    concurrently and repeatedly. If lock ordering were inconsistent, this
    would eventually deadlock (a slow/hung request or a 500 from MySQL)."""
    print("\n=== Deadlock avoidance test ===")

    unique = uuid.uuid4().hex[:8]
    carol = sign_up(client, f"carol_{unique}")
    dave = sign_up(client, f"dave_{unique}")
    deposit(client, carol["account"]["id"], 1000)
    deposit(client, dave["account"]["id"], 1000)

    rounds = 30
    errors = 0
    with ThreadPoolExecutor(max_workers=2 * rounds) as pool:
        futures = []
        for _ in range(rounds):
            futures.append(
                pool.submit(
                    transfer, client, carol["access_token"], carol["account"]["id"], dave["account"]["id"], 1
                )
            )
            futures.append(
                pool.submit(
                    transfer, client, dave["access_token"], dave["account"]["id"], carol["account"]["id"], 1
                )
            )
        for future in as_completed(futures):
            response = future.result()
            if response.status_code != 200:
                errors += 1
                print(f"  unexpected status {response.status_code}: {response.text}")

    print(f"{2 * rounds} opposite-direction transfers completed, {errors} errors.")
    assert errors == 0, "Some transfers failed/deadlocked — check lock ordering."
    print("PASS — no deadlocks across opposite-direction concurrent transfers.")


if __name__ == "__main__":
    with httpx.Client(timeout=TIMEOUT) as client:
        test_overdraft_race(client)
        test_deadlock_avoidance(client)
    print("\nAll concurrency tests passed.")
