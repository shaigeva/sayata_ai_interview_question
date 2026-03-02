# Technical Specification — Sayata Interview Question

## Project Structure

```
python_question/
├── pyproject.toml                  # uv-managed, all dependencies
├── Dockerfile                      # Single container: all servers
├── docker-compose.yml              # One-command startup
├── README.md                       # Candidate instructions
├── docs/
│   └── domain.md                   # Domain/business rules doc (large, with buried rules)
├── src/
│   └── sayata/
│       ├── __init__.py
│       ├── server.py               # Candidate's FastAPI server (main app)
│       ├── models.py               # Pydantic models (Submission, Quote, BindRequest, etc.)
│       ├── carriers/
│       │   ├── __init__.py
│       │   ├── base.py             # Base carrier client interface
│       │   ├── carrier_a.py        # Carrier A client (synchronous, has /options)
│       │   └── carrier_b.py        # Carrier B client (synchronous, comma-formatted prices)
│       └── simulators/
│           ├── __init__.py
│           ├── runner.py           # Starts all carrier simulators on different ports
│           ├── carrier_a_sim.py    # Carrier A simulator (FastAPI app)
│           ├── carrier_b_sim.py    # Carrier B simulator (FastAPI app)
│           ├── carrier_c_sim.py    # Carrier C simulator (polling-based)
│           └── carrier_d_sim.py    # Carrier D simulator (unfamiliar API shape)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures (base URL, etc.)
│   ├── test_stub.py                # Stub test importing from src (pre-configured for candidate)
│   └── test_verification.py        # Full verification test script (requests-based)
└── scripts/
    └── start.py                    # Entry point: starts simulators + candidate server
```

## Technology Stack

- **Python 3.12+**
- **FastAPI** — both for the candidate's server and carrier simulators
- **uvicorn** — ASGI server
- **httpx** — HTTP client for server-to-carrier communication
- **pydantic** — data models
- **pytest** — testing framework
- **requests** — used in test scripts for real HTTP calls
- **uv** — package management

## Port Assignments

| Service            | Port |
| ------------------ | ---- |
| Candidate's server | 8000 |
| Carrier A          | 8001 |
| Carrier B          | 8002 |
| Carrier C          | 8003 |
| Carrier D          | 8004 |

## Data Models

### Submission

```python
class Submission(BaseModel):
    id: str                     # Generated UUID
    business_name: str
    industry: str
    annual_revenue: float
    requested_limit: float      # Max payout requested
    requested_retention: float  # Deductible requested
    status: str = "created"     # "created" | "quoted"
```

### Quote

```python
class Quote(BaseModel):
    carrier: str                # "carrier_a", "carrier_b", etc.
    premium: float
    limit: float
    retention: float
    quote_id: str               # Carrier's quote reference
```

### BindRequest / BindResponse

```python
class BindRequest(BaseModel):
    quote_id: str
    carrier: str

class BindResponse(BaseModel):
    status: str                 # "bound"
    quote_id: str
    carrier: str
```

## Candidate's Server API

### POST /submissions

Create a new submission. Sends quote requests to all configured carriers.

**Request body:**
```json
{
    "business_name": "Acme Corp",
    "industry": "technology",
    "annual_revenue": 5000000,
    "requested_limit": 1000000,
    "requested_retention": 50000
}
```

**Response (201):**
```json
{
    "id": "uuid-here",
    "status": "created"
}
```

**Behavior:** On creation, the server immediately requests quotes from all
configured carriers (Carrier A and Carrier B in the skeleton). Quotes are fetched
synchronously and stored in memory.

### GET /submissions/{id}

Retrieve a submission and its quotes.

**Response (200):**
```json
{
    "id": "uuid-here",
    "business_name": "Acme Corp",
    "industry": "technology",
    "annual_revenue": 5000000,
    "requested_limit": 1000000,
    "requested_retention": 50000,
    "status": "quoted",
    "quotes": [
        {
            "carrier": "carrier_a",
            "premium": 15000,
            "limit": 1000000,
            "retention": 50000,
            "quote_id": "qa-123"
        },
        {
            "carrier": "carrier_b",
            "premium": 12500,
            "limit": 1000000,
            "retention": 50000,
            "quote_id": "qb-456"
        }
    ]
}
```

### POST /submissions/{id}/bind

Bind (accept) a specific quote.

**Request body:**
```json
{
    "quote_id": "qa-123",
    "carrier": "carrier_a"
}
```

**Response (200):**
```json
{
    "status": "bound",
    "quote_id": "qa-123",
    "carrier": "carrier_a"
}
```

**Behavior:** Sends a bind request to the appropriate carrier's API.

## Carrier Simulator Specifications

### Carrier A — Synchronous with Options Endpoint

**Port:** 8001

#### POST /quotes

Request a quote.

**Request body:**
```json
{
    "business_name": "Acme Corp",
    "industry": "technology",
    "annual_revenue": 5000000,
    "limit": 1000000,
    "retention": 50000
}
```

**Response (200) — success:**
```json
{
    "quote_id": "ca-uuid",
    "premium": 15000,
    "limit": 1000000,
    "retention": 50000
}
```

**Response (200) — limit/retention not supported:**
```json
{
    "error": "requested limit not available",
    "message": "The requested limit of 5000000 is not available. Check GET /options for supported values."
}
```

This is the intentional bug for Task 2: the server returns HTTP 200 even for
errors, and the candidate's server naively trusts the status code.

#### GET /options

Returns supported limit and retention values.

**Response (200):**
```json
{
    "supported_limits": [500000, 1000000, 2000000, 3000000],
    "supported_retentions": [25000, 50000, 100000, 250000]
}
```

#### POST /bind

Bind a quote.

**Request body:**
```json
{
    "quote_id": "ca-uuid"
}
```

**Response (200):**
```json
{
    "status": "bound",
    "quote_id": "ca-uuid"
}
```

#### GET /status

Health check / inspection endpoint.

**Response (200):**
```json
{
    "carrier": "carrier_a",
    "status": "running",
    "quotes_issued": 5,
    "binds_completed": 1
}
```

### Carrier B — Synchronous with Comma-Formatted Prices

**Port:** 8002

#### POST /quotes

Request a quote. Same request body as Carrier A.

**Response (200):**
```json
{
    "quote_id": "cb-uuid",
    "premium": "2,343",
    "limit": 1000000,
    "retention": 50000
}
```

**Key behavior:** Premium is returned as a **comma-formatted string** (e.g.,
`"2,343"` not `2343`). For values under $1,000, there's no comma so `int("500")`
works fine. For values >= $1,000, `int("2,343")` throws `ValueError`.

**Premium calculation must be deterministic:** The premium should be derived from
the submission data in a predictable way so that specific submissions reliably
produce premiums above or below $1,000. A simple formula:

```
premium = annual_revenue * rate_by_industry
```

With industry rates set so that, e.g.:
- `technology` with `annual_revenue=500000` → premium ~$800 (under $1,000, works)
- `technology` with `annual_revenue=5000000` → premium ~$8,000 (over $1,000, breaks)

#### POST /bind

Same interface as Carrier A.

#### GET /status

Same interface as Carrier A.

### Carrier C — Polling-Based (Task 3)

**Port:** 8003

This carrier is running from the start but NOT integrated into the candidate's
server. The candidate must add the integration.

#### POST /quotes

Submit a quote request. Returns immediately with a quote ID (not the actual
quote).

**Request body:** Same as Carrier A.

**Response (202):**
```json
{
    "quote_id": "cc-uuid",
    "status": "pending",
    "poll_url": "/quotes/cc-uuid"
}
```

#### GET /quotes/{quote_id}

Poll for quote status.

**Response — pending (200):**
```json
{
    "quote_id": "cc-uuid",
    "status": "pending"
}
```

**Response — ready (200):**
```json
{
    "quote_id": "cc-uuid",
    "status": "ready",
    "premium": 14200,
    "limit": 1000000,
    "retention": 50000
}
```

The simulator should introduce a configurable delay (e.g., 2–5 seconds) before
the quote becomes ready.

#### POST /bind

Same interface as Carrier A.

#### GET /status

Same interface as Carrier A.

### Carrier D — Unfamiliar API Shape (Task 4)

**Port:** 8004

This carrier is running from the start but NOT integrated. It uses completely
different field names and endpoint structure. Minimal documentation provided to
the candidate.

#### POST /api/v1/insurance-request

Submit a quote request (different endpoint path, different field names).

**Request body:**
```json
{
    "company": "Acme Corp",
    "sector": "technology",
    "revenue": 5000000,
    "coverage_amount": 1000000,
    "deductible": 50000
}
```

**Response (200):**
```json
{
    "request_id": "cd-uuid",
    "annual_cost": 11800,
    "max_coverage": 1000000,
    "deductible_amount": 50000,
    "provider": "carrier_d"
}
```

#### POST /api/v1/accept

Bind a quote (different endpoint, different field names).

**Request body:**
```json
{
    "request_id": "cd-uuid"
}
```

**Response (200):**
```json
{
    "confirmation": "accepted",
    "request_id": "cd-uuid"
}
```

#### GET /api/v1/info

Inspection endpoint (different path and response shape).

**Response (200):**
```json
{
    "service": "carrier_d",
    "version": "1.0",
    "endpoints": [
        {"method": "POST", "path": "/api/v1/insurance-request"},
        {"method": "POST", "path": "/api/v1/accept"},
        {"method": "GET", "path": "/api/v1/info"}
    ]
}
```

The `/info` endpoint is a breadcrumb for AI-driven exploration — it lists
available endpoints. A candidate (or their AI) who hits this first will
immediately understand the API shape.

## Candidate's Server — Skeleton Implementation Details

### Deliberate Bugs (Pre-planted)

**Bug 1 (Task 1) — Silent exception swallowing in Carrier B client:**

```python
# In carriers/carrier_b.py
async def get_quote(self, submission: Submission) -> Quote | None:
    response = await self.client.post(f"{self.base_url}/quotes", json={...})
    try:
        data = response.json()
        return Quote(
            carrier="carrier_b",
            premium=int(data["premium"]),  # Fails on "2,343"
            limit=data["limit"],
            retention=data["retention"],
            quote_id=data["quote_id"],
        )
    except Exception:
        # TODO: improve error handling
        return None
```

**Bug 2 (Task 2) — Naive status code check in Carrier A client:**

```python
# In carriers/carrier_a.py
async def get_quote(self, submission: Submission) -> Quote | None:
    response = await self.client.post(f"{self.base_url}/quotes", json={...})
    if response.status_code == 200:
        data = response.json()
        return Quote(
            carrier="carrier_a",
            premium=data["premium"],
            limit=data["limit"],
            retention=data["retention"],
            quote_id=data["quote_id"],
        )
    return None
```

The problem: when the limit is too high, Carrier A still returns 200 but with an
error body (`{"error": "...", "message": "..."}`). Accessing `data["premium"]`
raises `KeyError`, which is unhandled. The proper fix is to check for the error
field, then use `GET /options` to find the closest supported limit/retention.

### In-Memory State

```python
# Simple dict-based storage in server.py
submissions: dict[str, Submission] = {}
quotes: dict[str, list[Quote]] = {}  # submission_id -> quotes
```

### Carrier Registration

The skeleton registers Carrier A and Carrier B only. Carrier C and D are running
but not wired in — the candidate adds them.

```python
# In server.py
CARRIERS = [
    CarrierAClient(base_url="http://localhost:8001"),
    CarrierBClient(base_url="http://localhost:8002"),
]
```

## Docker Setup

### Dockerfile

Single Dockerfile that:
1. Uses Python 3.12 base image
2. Installs uv
3. Installs project dependencies via uv
4. Copies source code
5. Entry point runs `scripts/start.py`

### scripts/start.py

Starts everything in one process using uvicorn programmatically:

```python
import asyncio
import uvicorn

async def main():
    # Start carrier simulators
    configs = [
        uvicorn.Config("sayata.simulators.carrier_a_sim:app", host="0.0.0.0", port=8001),
        uvicorn.Config("sayata.simulators.carrier_b_sim:app", host="0.0.0.0", port=8002),
        uvicorn.Config("sayata.simulators.carrier_c_sim:app", host="0.0.0.0", port=8003),
        uvicorn.Config("sayata.simulators.carrier_d_sim:app", host="0.0.0.0", port=8004),
        uvicorn.Config("sayata.server:app", host="0.0.0.0", port=8000),
    ]
    servers = [uvicorn.Server(config) for config in configs]
    await asyncio.gather(*(server.serve() for server in servers))

if __name__ == "__main__":
    asyncio.run(main())
```

### docker-compose.yml

Simple single-service compose file:

```yaml
services:
  sayata:
    build: .
    ports:
      - "8000:8000"
      - "8001:8001"
      - "8002:8002"
      - "8003:8003"
      - "8004:8004"
```

## Test Specifications

### test_stub.py — Pre-configured for Candidates

A minimal test that imports from the codebase and runs, proving the test
infrastructure works:

```python
from sayata.models import Submission, Quote

def test_models_importable():
    """Verify test infrastructure is working."""
    sub = Submission(
        id="test-id",
        business_name="Test Corp",
        industry="technology",
        annual_revenue=1000000,
        requested_limit=1000000,
        requested_retention=50000,
    )
    assert sub.business_name == "Test Corp"
```

### test_verification.py — Full Verification Script

Uses `requests` to send real HTTP calls to the running servers. This is the
primary verification mechanism.

```python
import requests

BASE_URL = "http://localhost:8000"

def test_basic_flow():
    """Skeleton flow: submit, get quotes, bind."""
    # Create submission — low revenue so Carrier B premium < $1,000
    resp = requests.post(f"{BASE_URL}/submissions", json={
        "business_name": "Small Tech Co",
        "industry": "technology",
        "annual_revenue": 500000,
        "requested_limit": 1000000,
        "requested_retention": 50000,
    })
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    # Get quotes — should have 2 (one from each carrier)
    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["quotes"]) == 2

    # Bind first quote
    quote = data["quotes"][0]
    resp = requests.post(f"{BASE_URL}/submissions/{submission_id}/bind", json={
        "quote_id": quote["quote_id"],
        "carrier": quote["carrier"],
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "bound"


def test_task1_high_value_policy():
    """Task 1: High revenue submission should still return 2 quotes.

    Currently FAILS — Carrier B returns comma-formatted prices for
    premiums >= $1,000, and parsing breaks silently.
    """
    resp = requests.post(f"{BASE_URL}/submissions", json={
        "business_name": "Big Tech Corp",
        "industry": "technology",
        "annual_revenue": 5000000,
        "requested_limit": 1000000,
        "requested_retention": 50000,
    })
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    assert len(data["quotes"]) == 2, (
        f"Expected 2 quotes but got {len(data['quotes'])}. "
        f"Check carrier responses for parsing issues."
    )


def test_task2_high_limit_request():
    """Task 2: High limit request should still return 2 quotes.

    Currently FAILS — Carrier A returns 200 with error body for
    unsupported limits, and the server doesn't handle it.
    """
    resp = requests.post(f"{BASE_URL}/submissions", json={
        "business_name": "Large Enterprise",
        "industry": "manufacturing",
        "annual_revenue": 2000000,
        "requested_limit": 5000000,
        "requested_retention": 50000,
    })
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    assert len(data["quotes"]) == 2, (
        f"Expected 2 quotes but got {len(data['quotes'])}. "
        f"Check if all carriers are responding correctly."
    )


def test_task3_polling_carrier():
    """Task 3: Submission should include a quote from Carrier C (polling).

    Requires Carrier C integration — the candidate must add it.
    """
    resp = requests.post(f"{BASE_URL}/submissions", json={
        "business_name": "Medium Co",
        "industry": "technology",
        "annual_revenue": 3000000,
        "requested_limit": 1000000,
        "requested_retention": 50000,
    })
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    # Wait for polling to complete
    import time
    time.sleep(10)

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_c" in carriers, (
        f"Expected a quote from carrier_c but got quotes from: {carriers}"
    )


def test_task4_unfamiliar_carrier():
    """Task 4: Submission should include a quote from Carrier D (unfamiliar API).

    Requires Carrier D integration — the candidate must explore and add it.
    """
    resp = requests.post(f"{BASE_URL}/submissions", json={
        "business_name": "Another Corp",
        "industry": "technology",
        "annual_revenue": 2000000,
        "requested_limit": 1000000,
        "requested_retention": 50000,
    })
    assert resp.status_code == 201
    submission_id = resp.json()["id"]

    resp = requests.get(f"{BASE_URL}/submissions/{submission_id}")
    data = resp.json()
    carriers = [q["carrier"] for q in data["quotes"]]
    assert "carrier_d" in carriers, (
        f"Expected a quote from carrier_d but got quotes from: {carriers}"
    )
```

## Premium Calculation (Carrier Simulators)

All carriers use a deterministic formula so that specific submissions produce
predictable premiums:

```
base_rate = {
    "technology": 0.0016,
    "manufacturing": 0.0022,
    "retail": 0.0018,
    "healthcare": 0.0025,
    "finance": 0.0020,
}

premium = annual_revenue * base_rate[industry] * (limit / 1_000_000) * (1 + retention / limit)
```

Each carrier applies a slight multiplier (e.g., Carrier A: 1.0, Carrier B: 0.95,
Carrier C: 1.1, Carrier D: 0.9) to differentiate their prices.

This ensures:
- `technology, revenue=500000, limit=1M, retention=50K` → ~$840 (under $1,000 for Carrier B → no comma)
- `technology, revenue=5000000, limit=1M, retention=50K` → ~$8,400 (over $1,000 for Carrier B → has comma → bug triggers)

## Carrier A — Supported Options

```python
SUPPORTED_LIMITS = [500_000, 1_000_000, 2_000_000, 3_000_000]
SUPPORTED_RETENTIONS = [25_000, 50_000, 100_000, 250_000]
```

Carrier A rejects limits/retentions not in these lists with a 200 + error body.
The "closest option" business rule means the candidate's server should map to the
nearest supported value.
