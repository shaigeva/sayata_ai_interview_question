# Sayata Quoting Platform — Interview Exercise

Welcome! In this exercise you'll work with a simplified insurance quoting
platform. The system takes business details, fetches quotes from multiple
insurance carriers, and lets users accept (bind) a quote.

A working skeleton is already in place — your job is to fix bugs and add new
carrier integrations.

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Install dependencies

```bash
uv sync
```

### Start all servers

This starts the candidate server (port 8000) and four carrier simulators
(ports 8001–8004) in a single process:

```bash
uv run python scripts/start.py
```

### Alternative: Docker

```bash
docker compose up --build
```

## Verify your work

With servers running, open a second terminal and run the test suite:

```bash
uv run pytest tests/test_verification.py -v
```

You should see `test_basic_flow` pass. The remaining tests will fail — fixing
them is your job.

You can also run the unit tests (no servers needed):

```bash
uv run pytest tests/test_stub.py -v
```

## Architecture

```
You (candidate)              Carrier Simulators
┌──────────────┐            ┌───────────────────┐
│  server.py   │───────────▶│ Carrier A  :8001   │
│  (port 8000) │───────────▶│ Carrier B  :8002   │
│              │            │ Carrier C  :8003   │
│              │            │ Carrier D  :8004   │
└──────────────┘            └───────────────────┘
```

- **Your server** (`src/sayata/server.py`) receives submissions, fetches quotes
  from carriers, and handles binds.
- **Carrier simulators** are local mock APIs that behave like real insurance
  carrier systems. They're read-only for you — don't modify them.
- **Carrier clients** (`src/sayata/carriers/`) contain the logic for calling each
  carrier's API.

Currently, only Carrier A and Carrier B are integrated. Carriers C and D are
running but not connected.

## Tasks

### Task 1: Bug — Quotes Missing for High-Value Policies

When submitting a business with high annual revenue ($5M+), only 1 quote is
returned instead of 2. Something is going wrong with one of the carrier
integrations.

**Verify:** `test_task1_high_value_policy` should pass.

### Task 2: Bug — Quotes Missing for High-Limit Requests

When requesting a high coverage limit ($5M), only 1 quote is returned instead
of 2. A carrier is failing but it's not immediately obvious why.

Read the domain document (`docs/domain.md`) for relevant business rules on how
to handle this properly.

**Verify:** `test_task2_high_limit_request` should pass.

### Task 3: Feature — Integrate Carrier C (Polling-Based)

Carrier C is running on port 8003 but not integrated. Unlike Carriers A and B,
it doesn't return quotes immediately — you'll need to figure out its API pattern
and implement the integration.

**Verify:** `test_task3_polling_carrier` should pass.

### Task 4: Feature — Integrate Carrier D (Unfamiliar API)

Carrier D is running on port 8004 but not integrated. It uses a completely
different API structure from the other carriers. You'll need to explore its
endpoints and figure out how to integrate it.

**Hint:** Most APIs have a way to describe themselves.

**Verify:** `test_task4_unfamiliar_carrier` should pass.

## Reference

- Domain document with business rules: `docs/domain.md`
- Carrier client interface: `src/sayata/carriers/base.py`
- Existing carrier clients: `src/sayata/carriers/carrier_a.py`, `carrier_b.py`

## Notes

- You're expected to use AI tooling (Cursor, Copilot, Claude Code, etc.).
- You can ask the interviewers questions at any time.
- Tasks are independent — you can work on them in any order or in parallel.
- You're not expected to finish everything. Do what you can.
