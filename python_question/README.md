# Sayata Quoting Platform — Interview Exercise

Welcome! In this exercise you'll work with a simplified insurance quoting
platform. The system takes business details, fetches quotes from multiple
insurance carriers, and lets users accept (bind) a quote.

A working skeleton is already in place — your job is to fix bugs and add new
carrier integrations.

## Important info

- You're expected to use AI tooling (Cursor, Copilot, Claude Code, etc.).
- You can ask the interviewers questions at any time.
- Tasks are independent — you can work on them in any order or in parallel.
- Finishing all tasks is a plus, but it's not the only evaluation criterion. Do what you can.

## Setup

### Prerequisites

- Python 3.12 (exactly — not 3.13+)
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

## Verify your work

With servers running, open a second terminal and run the verification script:

```bash
uv run python scripts/verify.py
```

This sends a few requests to the running server and prints the results so you
can quickly check what's working.

### Testing

pytest is pre-installed and a stub test file is provided at `tests/test_stub.py`
to prove the infrastructure works. If you choose to write tests, you can use it
as a starting point:

```bash
uv run pytest tests/ -v
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

Your tasks are described in the `tickets/` directory. Work through them in any
order:

| Ticket | Type | Description |
|--------|------|-------------|
| [ticket-1](tickets/candidate/ticket-1.md) | Bug | Quotes missing for high-value policies |
| [ticket-2](tickets/candidate/ticket-2.md) | Bug | Quotes missing for high-limit requests |
| [ticket-3](tickets/candidate/ticket-3.md) | Feature | Integrate Carrier C |
| [ticket-4](tickets/candidate/ticket-4.md) | Feature | Integrate Carrier D |

## Reference

- Platform architecture: `docs/architecture.md`
- Business rules & principles: `docs/business-rules.md`
- Insurance glossary: `docs/glossary.md`
- UX & frontend reference: `docs/frontend-guidelines.md`
- Carrier client interface: `src/sayata/carriers/base.py`
- Existing carrier clients: `src/sayata/carriers/carrier_a.py`, `carrier_b.py`

## After the Interview

If asked to submit your solution:

```bash
zip -r solution.zip . -x '.venv/*' '__pycache__/*' 'packages/*'
```
