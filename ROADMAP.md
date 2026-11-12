# Roadmap

Goal: make this project interview-ready (correct, tested, documented, deployed),
then grow it with features that show off payments-domain depth.

Work top to bottom — each phase builds on the one before it. One PR per bullet
group keeps history readable (interviewers do look at commit history).

---

## Phase 0 — Security fixes (do first, ~1 day)

- [ ] Require auth on `GET /accounts/{id}` and only allow the owner to read it
- [ ] Require auth on `GET /accounts/{id}/transfers` (owner only) — currently anyone with an account id can read balance + history
- [ ] Require auth on `POST /accounts/`; take `owner_id` from the token, never from the request body
- [ ] Audit every remaining route for missing `get_current_user` (users/search, recipient lookup)
- [ ] Fail startup if `JWT_SECRET` is missing or a known default
- [ ] Stop publishing the MySQL port in `docker-compose.yml` by default

## Phase 1 — Money correctness (~1–2 days)

- [ ] **Idempotency race:** wrap the insert in try/except `IntegrityError` → rollback → re-read and return the existing `transfer_id` (today a concurrent duplicate returns a 500)
- [ ] **Key reuse with different payload:** store a request hash (sender, receiver, amount) with the key; mismatch → 422
- [ ] Accept `amount` as `Decimal` in Pydantic schemas (`gt=0`, `max_digits=18`, `decimal_places=2`); remove the float→Decimal conversion in the service
- [ ] Fix ORM type hints: `Mapped[Decimal]` not `Mapped[float]` for balance/amount
- [ ] Reject self-transfers (sender == receiver)
- [ ] Apply the same locking + idempotency rules to deposits
- [ ] Add a DB `CHECK (balance >= 0)` constraint as a last line of defense

## Phase 2 — Tests (~2–3 days)

- [ ] Set up `pytest` with fixtures: test DB, `TestClient`, user/account factories
- [ ] Unit tests for `TransferService`: happy path, insufficient funds, zero/negative amount, wrong owner, self-transfer, idempotent replay, key mismatch
- [ ] Unit tests for `UserService`, `FriendService`, `AccountService`
- [ ] API tests: auth required on every protected route, correct status codes
- [ ] **Invariant test:** for every account, `balance == sum(credits) - sum(debits)`; total money in the system only changes on deposit
- [ ] Move `scripts/concurrency_test.py` into a pytest integration suite against real MySQL (testcontainers or the compose DB), marked `@pytest.mark.integration`
- [ ] Frontend: Vitest + React Testing Library for SendMoneyModal, DepositModal, login flow
- [ ] Coverage report (`pytest-cov`), target ≥ 80% on `services/`

## Phase 3 — Engineering hygiene (~2 days)

- [ ] **Alembic** migrations; remove `Base.metadata.create_all` from startup; generate the initial migration from current models
- [ ] Clean up: delete `defenseLayer.sql`, the root `Requirements.txt` and unused `psycopg2-binary`; rename `DockerFile` → `Dockerfile`; move run notes out of requirements
- [ ] Split deps into `requirements.txt` and `requirements-dev.txt`, or switch to `pyproject.toml` + `uv`
- [ ] Linting/formatting: `ruff` (lint + format) for Python, eslint + prettier for frontend, `pre-commit` hooks
- [ ] Consistent snake_case naming (`senderAccount` → `sender_account`)
- [ ] `/health` endpoint (checks DB) and wire it into the compose healthcheck
- [ ] Structured JSON logs with a request ID per request
- [ ] Global error shape: `{ "error": { "code": "...", "message": "..." } }`
- [ ] Pagination (cursor-based) on transaction history

## Phase 4 — CI/CD + docs + deploy (~2 days)

- [ ] GitHub Actions: ruff + pytest (with a MySQL service container) + frontend lint/test/build on every push/PR
- [ ] Build Docker images in CI to catch broken Dockerfiles
- [ ] **Root README.md:** pitch, screenshot/GIF, quickstart, architecture diagram, tech stack, **Design Decisions** (double-entry ledger, lock ordering, idempotency, Decimal), testing instructions, known limitations
- [ ] `docs/` folder: ER diagram, transfer sequence diagram, API overview (link to `/docs`)
- [ ] Deploy (Render / Fly.io / Railway + managed MySQL), with a live demo link and a seeded demo account in the README
- [ ] CI badge + coverage badge in README

## Phase 5 — Security hardening (~2 days)

- [ ] Rate limiting on `/login`, `/users/` signup, and transfers (`slowapi`, Redis-backed)
- [ ] Short-lived access token + refresh token in httpOnly cookie; logout / token revocation
- [ ] Password rules + account lockout after N failed logins
- [ ] Security headers in nginx (CSP, HSTS, X-Frame-Options)
- [ ] Audit log table: who did what, when, from which IP
- [ ] Optional: TOTP 2FA

---

## Phase 6 — New features

Ordered by interview value per hour of work. Each one demonstrates a specific
skill — that's the story to tell for it.

### Tier 1 — High value, builds on what exists

- [ ] **Payment requests** — "Request $20 from Sam." New `payment_requests` table with a state machine `PENDING → PAID | DECLINED | CANCELLED | EXPIRED`; paying a request runs a normal transfer. *Shows: state machines, valid-transition enforcement.*
- [ ] **Memos + activity feed** — note on each transfer ("🍕 pizza"), a Venmo-style feed of friends' activity with privacy settings (public / friends / private). *Shows: query design, authorization rules.*
- [ ] **Real-time notifications** — WebSocket push when you receive money or a request ("Alex sent you $15"), plus a notifications table and unread badge in the Navbar. *Shows: async, WebSockets, pub/sub.*
- [ ] **Withdrawals** — the inverse of deposit, with locking + idempotency. *Shows: reuse of ledger primitives.*
- [ ] **Refunds / reversals** — reverse a transfer by posting compensating ledger entries (never edit or delete rows); uses the existing `REVERSED` status. *Shows: immutable ledger, accounting correctness.*

### Tier 2 — Strong differentiators

- [ ] **Stripe (test mode) deposits** — top up via Stripe Checkout; credit the account only from a **webhook** with signature verification and event-id idempotency. *Shows: third-party integration, webhooks, exactly-once processing. Top interview topic.*
- [ ] **Split a bill / groups** — create a group, split an expense evenly or by custom amounts, generate payment requests per member, track who has paid. *Shows: domain modeling, rounding (distributing leftover cents).*
- [ ] **Scheduled & recurring payments** — "Pay rent $500 on the 1st." Background worker (APScheduler, or Celery + Redis) with retries; failures surface as notifications. *Shows: background jobs, retries, idempotent workers.*
- [ ] **Transfer limits & fraud rules** — daily send limit, velocity checks (N transfers / minute), large transfers held as `PENDING` for review. *Shows: risk thinking, a `PENDING` flow.*
- [ ] **Reconciliation job + admin dashboard** — nightly job compares cached balances to ledger sums and flags drift; admin role sees users, holds, flagged transfers. *Shows: RBAC, operational maturity.*

### Tier 3 — Polish / nice-to-have

- [ ] Statements: monthly CSV / PDF export of transactions
- [ ] Spending insights: charts by month / by friend on the dashboard
- [ ] Pay links + QR codes (`/pay/username?amount=20`)
- [ ] User profiles: display name, avatar upload, friend requests with accept/decline (instead of instant add)
- [ ] Multi-currency wallets with FX conversion (the `currency` column already exists)
- [ ] Email notifications (dev: MailHog in compose)
- [ ] Dark mode, mobile-responsive pass, loading skeletons, toast notifications

---

## Suggested order of attack

1. Phase 0 + Phase 1 → bugs fixed
2. Phase 2 → tests prove it (write the race test *before* the fix to show it failing)
3. Phase 3 + 4 → README, CI, live deploy — **the project is interview-ready here**
4. Phase 6 Tier 1: payment requests → notifications → refunds
5. Phase 5 hardening alongside
6. Phase 6 Tier 2: Stripe webhooks → split bills → scheduled payments

## Interview talking points to prepare

- Why a double-entry ledger instead of just updating balances?
- How do you prevent double-spend under concurrency? Why lock in id order?
- What happens if a client retries a transfer? If two retries arrive at once?
- Why Decimal, never float, for money?
- How would you scale this (read replicas, sharding by account, event sourcing, outbox pattern)?
- How do you guarantee a Stripe webhook credits an account exactly once?
