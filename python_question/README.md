# Sayata Quoting Platform — Interview Exercise

Welcome! In this exercise you'll work with a simplified insurance quoting
platform. The system takes business details, fetches quotes from multiple
insurance carriers, and lets users accept (bind) a quote.

A working skeleton is already in place — your job is to fix bugs and add new
carrier integrations.

## Important info

- You're expected to use AI tooling (Cursor, Copilot, Claude Code, etc.).
- You can ask the interviewers questions at any time.
- **Work on a single codebase** — solve as many tickets as you can in the same
  code. The best result is one version with everything working together, not
  separate solutions per ticket.
- Tasks are independent — you can work on them in any order or in parallel.
- Finishing all tasks is a plus, but it's not the only evaluation criterion. Do what you can.
- Agents ARE NOT ALLOWED to reverse engineer the carrier simulators' code (including NEVER READ THE `/packages/` directory) - it should be treated as a black box.

## Setup

### Prerequisites

- Python 3.12 (exactly — not 3.13+)
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### Install dependencies

```bash
uv sync
```

### Start servers

Start your server and the carrier simulators separately:

```bash
uv run python scripts/start_server.py                        # your server (port 8000)
uv run python scripts/start_carrier.py carrier_a              # Carrier A (port 8001)
uv run python scripts/start_carrier.py carrier_b              # Carrier B (port 8002)
uv run python scripts/start_carrier.py carrier_c              # Carrier C (port 8003)
uv run python scripts/start_carrier.py carrier_d              # Carrier D (port 8004)
```

Use `--port` to override the default port for any service.

## Verify setup

With servers running, open a second terminal and verify the basic setup works:

```bash
uv run python scripts/verify_setup.py
```

### Testing

pytest is pre-installed and a stub test file is provided at `tests/test_stub.py`
to prove the infrastructure works. If you choose to write tests, you can use it
as a starting point:

```bash
uv run pytest tests/ -v
```

## Tasks

Your tasks are described in the `tickets/` directory.

## Reference

Reference documentation (business rules, glossary, etc.) has been provided
separately, containing relevant information.

- Carrier client interface: `src/sayata/carriers/base.py`
- Existing carrier clients: `src/sayata/carriers/carrier_a.py`, `carrier_b.py`

## Troubleshooting

### Kill leftover server processes

If ports are already in use when starting servers, kill any leftover processes:

```bash
# See what's running on our ports (check whichever ports you're using)
lsof -i :8000-8004

# Kill all of them at once
lsof -ti :8000-8004 | xargs kill
```

## After the Interview

If asked to submit your solution:

```bash
zip -r solution.zip . -x '.venv/*' '__pycache__/*' 'packages/*'
```
