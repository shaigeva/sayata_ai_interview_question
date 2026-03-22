# Sayata Interview Exercise — Environment Setup

Welcome! Before the interview, please set up your development environment
using the instructions below.

## Prerequisites

- **Python 3.12** (exactly — not 3.13+)
- **[uv](https://docs.astral.sh/uv/)** (Python package manager)

If you don't have Python 3.12 installed, uv can fetch it for you:

```bash
uv python install 3.12
```

## Setup

```bash
# Install dependencies
uv sync

# Run tests to verify
uv run pytest -v
```

You should see all tests pass, including a server health check.

## Verify server runs

```bash
# Start the stub server
uv run uvicorn sayata.server_stub:app --port 8000 &

# Check it responds
curl http://localhost:8000/health

# Stop it
kill %1
```

## AI Tools

You're expected to use AI tooling during the interview (Cursor, Copilot,
Claude Code, etc.). Please set up your preferred AI tools in this project
before the interview.

## What to Expect

During the interview you'll receive exercise materials (code and tickets as a
zip file) along with separate reference documentation. No exercise content is
included in this setup repo — this is just to ensure your environment is ready.
