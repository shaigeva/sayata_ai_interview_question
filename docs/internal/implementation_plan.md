# Implementation Plan — Sayata Interview Question

All work is in the `python_question/` directory.

## Phase 1: Project Scaffolding

### Step 1.1 — Initialize Python project with uv

- Create `pyproject.toml` with project metadata and dependencies:
  - fastapi
  - uvicorn
  - httpx
  - pydantic
  - pytest
  - requests (for test script)
- Set up `src/sayata/` package structure with `__init__.py` files.
- Verify `uv sync` works and dependencies install.

### Step 1.2 — Create data models

- Create `src/sayata/models.py` with Pydantic models:
  - `Submission` — business_name, industry, annual_revenue, requested_limit,
    requested_retention, id, status
  - `Quote` — carrier, premium, limit, retention, quote_id
  - `BindRequest` — quote_id, carrier
  - `BindResponse` — status, quote_id, carrier
  - `SubmissionResponse` — id, status
  - `SubmissionDetail` — full submission + list of quotes

## Phase 2: Carrier Simulators

### Step 2.1 — Carrier A simulator

Create `src/sayata/simulators/carrier_a_sim.py`:
- FastAPI app on port 8001.
- `POST /quotes` — accepts submission data, calculates premium using
  deterministic formula. Returns quote if limit/retention are in supported list.
  Returns HTTP 200 with error body if not supported (Task 2 setup).
- `GET /options` — returns supported limits and retentions.
- `POST /bind` — accepts quote_id, returns "bound".
- `GET /status` — returns carrier status and counters.
- In-memory store for issued quotes.

### Step 2.2 — Carrier B simulator

Create `src/sayata/simulators/carrier_b_sim.py`:
- FastAPI app on port 8002.
- `POST /quotes` — same as Carrier A, but returns premium as **comma-formatted
  string** (e.g., `"2,343"` not `2343`). This is the Task 1 bug trigger.
- All limits/retentions accepted (no /options complexity).
- `POST /bind`, `GET /status` — same as Carrier A.

### Step 2.3 — Carrier C simulator

Create `src/sayata/simulators/carrier_c_sim.py`:
- FastAPI app on port 8003.
- `POST /quotes` — returns 202 with `quote_id` and `status: "pending"`.
  Schedules a background task that makes the quote "ready" after a configurable
  delay (3 seconds default).
- `GET /quotes/{quote_id}` — returns current status. After delay, returns full
  quote with premium, limit, retention.
- `POST /bind`, `GET /status` — same pattern as others.

### Step 2.4 — Carrier D simulator

Create `src/sayata/simulators/carrier_d_sim.py`:
- FastAPI app on port 8004.
- Completely different API shape:
  - `POST /api/v1/insurance-request` instead of `/quotes`
  - Different field names: `company`, `sector`, `revenue`, `coverage_amount`,
    `deductible` instead of `business_name`, `industry`, etc.
  - Response uses `annual_cost` instead of `premium`, `max_coverage` instead of
    `limit`, etc.
- `POST /api/v1/accept` instead of `/bind`.
- `GET /api/v1/info` — lists available endpoints (breadcrumb for exploration).

### Step 2.5 — Simulator runner

Create `src/sayata/simulators/runner.py`:
- Utility to start all simulators programmatically using uvicorn.
- Used by both the startup script and optionally by tests.

## Phase 3: Candidate's Server (Skeleton)

### Step 3.1 — Base server with in-memory state

Create `src/sayata/server.py`:
- FastAPI app on port 8000.
- In-memory dicts for submissions and quotes.
- `POST /submissions` — creates submission, fetches quotes from carriers, stores
  results.
- `GET /submissions/{id}` — returns submission with quotes.
- `POST /submissions/{id}/bind` — sends bind to carrier, returns result.

### Step 3.2 — Carrier A client (with planted bug)

Create `src/sayata/carriers/carrier_a.py`:
- `get_quote(submission)` — sends POST to Carrier A, parses response.
- **Planted bug:** Checks `response.status_code == 200` and directly accesses
  `data["premium"]`. When Carrier A returns an error body (for unsupported
  limits), this raises `KeyError` — which is either unhandled or caught too
  broadly.
- `bind_quote(quote_id)` — sends bind request.

### Step 3.3 — Carrier B client (with planted bug)

Create `src/sayata/carriers/carrier_b.py`:
- `get_quote(submission)` — sends POST to Carrier B, parses response.
- **Planted bug:** Uses `int(data["premium"])` to parse premium. Works for
  `"500"`, fails for `"2,343"`. Wrapped in `try/except Exception: return None`
  with a misleading `# TODO: improve error handling` comment.
- `bind_quote(quote_id)` — sends bind request.

### Step 3.4 — Base carrier client

Create `src/sayata/carriers/base.py`:
- Abstract base class or protocol defining the carrier client interface:
  - `get_quote(submission) -> Quote | None`
  - `bind_quote(quote_id) -> BindResponse`

### Step 3.5 — Wire carriers into server

In `server.py`:
- Register Carrier A and Carrier B clients only.
- On submission creation, iterate registered carriers, call `get_quote` for each,
  collect results.
- Carrier C and D are NOT registered — the candidate adds them.

## Phase 4: Test Infrastructure

### Step 4.1 — conftest.py

Create `tests/conftest.py`:
- Fixtures for base URL (defaults to `http://localhost:8000`).
- Any shared test utilities.

### Step 4.2 — Stub test

Create `tests/test_stub.py`:
- Imports `Submission` and `Quote` from `sayata.models`.
- Single test that creates a model instance and asserts a field — proves the test
  setup works.
- This is what the candidate sees first, giving them a working test to build on.

### Step 4.3 — Verification test script

Create `tests/test_verification.py`:
- Full test suite using `requests` against running servers.
- `test_basic_flow` — the happy path (low revenue, standard limits). Should
  PASS with skeleton.
- `test_task1_high_value_policy` — high revenue triggers Carrier B comma bug.
  Should FAIL until candidate fixes it.
- `test_task2_high_limit_request` — high limit triggers Carrier A error body.
  Should FAIL until candidate fixes it.
- `test_task3_polling_carrier` — checks for Carrier C quote. Should FAIL until
  candidate integrates Carrier C.
- `test_task4_unfamiliar_carrier` — checks for Carrier D quote. Should FAIL
  until candidate integrates Carrier D.
- Clear assertion messages that hint at the problem without giving it away.

## Phase 5: Infrastructure

### Step 5.1 — Startup script

Create `scripts/start.py`:
- Starts all 5 servers (4 simulators + candidate server) in one process using
  asyncio + uvicorn.
- Prints startup message with port assignments.
- This is the "one command to start everything."

### Step 5.2 — Dockerfile

Create `Dockerfile`:
- Based on `python:3.12-slim`.
- Install uv.
- Copy project, install deps.
- Entry point: `python scripts/start.py`.

### Step 5.3 — docker-compose.yml

Create `docker-compose.yml`:
- Single service exposing ports 8000–8004.
- Simple, minimal config.

## Phase 6: Documentation

### Step 6.1 — Domain document

Create `docs/domain.md`:
- "Sayata Quoting Platform — Architecture & Business Rules"
- 8–10 business principles, most irrelevant or already implemented.
- **Buried critical rule:** "Always try to offer the best quotes — if a carrier
  doesn't support a requested limit or retention, offer the closest available
  option."
- Insurance domain background, UX principles (irrelevant to backend), etc.
- Deliberately lengthy — the candidate should feed this to their AI and extract
  what matters.

### Step 6.2 — Candidate instructions (README)

Replace `README.md` with:
- What the repo is and what the domain is (brief).
- How to set up: install uv, `uv sync`, start servers.
- How to run with Docker (alternative).
- How to verify: run the test script.
- The task list — all 4 tasks described clearly.
- Reference to domain doc for business rules.
- Note that they're expected to use AI tooling.
- Note that they can ask interviewers questions.

## Phase 7: Validation

### Step 7.1 — Verify skeleton works

- Start all servers.
- Run `test_basic_flow` — must PASS.
- Run `test_task1_high_value_policy` — must FAIL (confirms bug is planted).
- Run `test_task2_high_limit_request` — must FAIL (confirms bug is planted).
- Run `test_task3_polling_carrier` — must FAIL (Carrier C not integrated).
- Run `test_task4_unfamiliar_carrier` — must FAIL (Carrier D not integrated).

### Step 7.2 — Verify each task is solvable

- Fix each bug / implement each feature independently to confirm:
  - Task 1 fix: Replace `int(data["premium"])` with
    `int(data["premium"].replace(",", ""))` → test passes.
  - Task 2 fix: Check for `"error"` in response, call `GET /options`, find
    closest limit/retention, re-request → test passes.
  - Task 3 implementation: Add Carrier C client with background polling → test
    passes after delay.
  - Task 4 implementation: Add Carrier D client mapping field names → test
    passes.
- Revert fixes after validation — the skeleton must ship with bugs intact.

### Step 7.3 — Docker build verification

- `docker compose up` starts everything.
- All tests produce expected pass/fail results from inside container.

## Implementation Order

The phases above are listed in dependency order. Within each phase, steps can
mostly be done in parallel. The critical path is:

1. Scaffolding (Phase 1) — everything depends on this.
2. Models (Step 1.2) — simulators and server both need these.
3. Simulators (Phase 2) and Server (Phase 3) can be done in parallel once models
   exist.
4. Tests (Phase 4) need both simulators and server.
5. Infrastructure (Phase 5) needs all code in place.
6. Documentation (Phase 6) can be written in parallel with any phase.
7. Validation (Phase 7) is last.

## Files to Create (Complete List)

```
python_question/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── README.md                          # Replace existing stub
├── docs/
│   └── domain.md
├── src/
│   └── sayata/
│       ├── __init__.py
│       ├── server.py
│       ├── models.py
│       ├── carriers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── carrier_a.py
│       │   └── carrier_b.py
│       └── simulators/
│           ├── __init__.py
│           ├── runner.py
│           ├── carrier_a_sim.py
│           ├── carrier_b_sim.py
│           ├── carrier_c_sim.py
│           └── carrier_d_sim.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_stub.py
│   └── test_verification.py
└── scripts/
    └── start.py
```

Total: ~22 files to create.
