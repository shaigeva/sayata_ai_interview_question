# AI Interview Exercise — Developer Guide

## What this project is

An interview exercise that evaluates backend candidates' **AI proficiency** — not just coding, but context curation, feedback loop setup, output review, and constraint awareness. Candidates fix bugs and integrate carrier APIs in a simplified insurance quoting platform.

## Project structure

```
ai_interview_question/
├── python_question/              # The exercise
│   ├── src/sayata/
│   │   ├── server.py             # Candidate's server (has bugs)
│   │   ├── models.py             # Pydantic models
│   │   ├── server_stub.py        # Skeleton stub server (pre-interview)
│   │   ├── carriers/             # Carrier clients (candidate edits these)
│   │   │   ├── base.py           # Abstract interface
│   │   │   ├── carrier_a.py      # Has bug (unsupported limit handling)
│   │   │   └── carrier_b.py      # Has bug (comma parsing)
│   │   └── simulators/           # Carrier simulators (SOURCE — never shipped)
│   │       ├── carrier_a_sim.py  # /quoting_options, /api_info, incompatible errors
│   │       ├── carrier_b_sim.py  # Mixed premium types (float < 1K, string >= 1K)
│   │       ├── carrier_c_sim.py  # Polling-based quotes
│   │       └── carrier_d_sim.py  # Different API shape
│   ├── scripts/
│   │   ├── start.py              # Interviewer-only: starts everything
│   │   ├── start_server.py       # Candidate: starts candidate server (--port)
│   │   ├── start_carrier.py      # Candidate: starts one carrier (carrier_id --port)
│   │   ├── verify_setup.py       # Candidate: tests each service individually
│   │   ├── prepare_delivery.sh   # Builds 4 delivery zips
│   │   ├── test_delivery.sh      # End-to-end test (16 checks)
│   │   └── build_simulators.sh   # Compiles simulators to .pyc wheel
│   ├── tests/
│   │   ├── interviewer/
│   │   │   └── test_verification.py  # 15 tests (never shipped to candidates)
│   │   ├── test_setup.py         # Skeleton tests (shipped in skeleton.zip)
│   │   ├── test_stub.py          # Exercise stub tests (shipped in exercise.zip)
│   │   └── conftest.py
│   ├── tickets/
│   │   ├── candidate/            # Candidate-facing tickets (shipped)
│   │   └── interviewer/          # Interviewer tickets with root causes (not shipped)
│   ├── docs/
│   │   ├── business-rules.md     # Shipped in docs.zip (critical for tickets 1+2)
│   │   ├── glossary.md           # Shipped in docs.zip (volume)
│   │   ├── frontend-guidelines.md # Shipped in docs.zip (integer premium trap)
│   │   ├── architecture.md       # NOT shipped — interviewer reference only
│   │   └── about.md              # Shipped in skeleton-docs.zip
│   ├── packages/                 # Built wheel goes here
│   ├── delivery/                 # Generated zips (gitignored)
│   ├── README.md                 # Exercise README (shipped)
│   ├── README_PREP.md            # Skeleton README (shipped)
│   ├── INTERVIEWER_GUIDE.md      # Full interviewer instructions
│   └── pyproject.toml
└── docs/internal/                # Planning docs (not part of exercise)
```

## Delivery pipeline (4 zips)

Run `bash python_question/scripts/prepare_delivery.sh` to produce:

| Zip | When | Contents |
|-----|------|----------|
| `skeleton.zip` | Days before interview | Code setup: pyproject.toml, server_stub, test_setup |
| `skeleton-docs.zip` | Days before interview | `docs/about.md` (separate from code) |
| `exercise.zip` | During interview | Code, tickets, start scripts, wheel. NO docs. |
| `docs.zip` | During interview | business-rules.md, glossary.md, frontend-guidelines.md |

## How to test

```bash
cd python_question

# Full delivery pipeline test (16 checks, uses BASE_PORT=9100)
bash scripts/test_delivery.sh

# Interviewer baseline tests against dev servers
uv run python scripts/start.py &
sleep 3
uv run pytest tests/interviewer/test_verification.py -v -k "basic_flow or submission_not_found or low_revenue"

# All interviewer tests (requires all tickets to be solved)
uv run pytest tests/interviewer/test_verification.py -v

# After ANY simulator change, rebuild the wheel:
bash scripts/build_simulators.sh
```

## Key traps in the exercise

### Ticket 1 — Carrier B regression trap
- Carrier B returns premium as float (798.0) for < $1K, comma string ("8,400") for >= $1K
- Naive fix `.replace(",", "")` crashes on the float (AttributeError)
- `frontend-guidelines.md` requires integer premiums — AI's `float()` fix violates this

### Ticket 2 — Discovery + direction trap
- Error message just says "incompatible option" — no endpoint hint
- Endpoint is `/quoting_options` (not `/options`)
- Carriers A/B use `/api_info` instead of `/docs` for Swagger UI
- Principle 5 in business-rules.md: limits round UP, retentions round DOWN
- Without docs, AI implements "closest value" → wrong direction

### Tickets 3/4 — API exploration
- Tickets mention `/docs` endpoint (works for C/D, not A/B)
- Principle 11 in business-rules.md mentions both `/docs` and `/api_info`

## Important conventions

- **Rebuild wheel after simulator changes:** `bash scripts/build_simulators.sh`
- **Python 3.12 exactly** — .pyc in wheel is version-specific
- **BASE_PORT env var** — all scripts honor it (default 8000)
- **Candidate scripts vs interviewer scripts** — candidates get `start_server.py` + `start_carrier.py`, NOT `start.py`
- **Docs are separate from code** — never add docs to exercise.zip
- **No root cause hints** in candidate-facing materials
- **Tickets name specific carriers** — "Carrier B's quote is not included", not "1 instead of 2"

## When making changes

After making changes, always:

1. **Rebuild the wheel** if you changed any simulator (`src/sayata/simulators/`)
2. **Run `bash scripts/test_delivery.sh`** to verify the delivery pipeline (16 checks)
3. **Run interviewer baseline tests** to verify the skeleton still works
4. **Update this CLAUDE.md** if you changed the project structure, delivery pipeline, traps, or conventions
5. **Update `INTERVIEWER_GUIDE.md`** if you changed anything that affects the interview flow
6. **Update memory files** in `~/.claude/projects/.../memory/` if you changed key design decisions
