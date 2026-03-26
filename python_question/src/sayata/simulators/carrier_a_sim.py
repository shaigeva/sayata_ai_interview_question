"""Carrier A simulator — synchronous quotes with quoting options endpoint.

Returns quotes instantly. Rejects unsupported limits/retentions with a 200 + error body
(not an HTTP error code). Exposes GET /quoting_options so callers can discover supported values.
"""

import uuid

from fastapi import FastAPI

app = FastAPI(title="Carrier A Simulator", docs_url="/api_info", redoc_url=None)

SUPPORTED_LIMITS = [500_000, 1_000_000, 2_000_000, 3_000_000]
SUPPORTED_RETENTIONS = [25_000, 50_000, 100_000, 250_000]

BASE_RATES = {
    "technology": 0.0016,
    "manufacturing": 0.0022,
    "retail": 0.0018,
    "healthcare": 0.0025,
    "finance": 0.0020,
}
CARRIER_MULTIPLIER = 1.0

quotes_store: dict[str, dict] = {}
stats = {"quotes_issued": 0, "binds_completed": 0}


def _calculate_premium(annual_revenue: float, industry: str, limit: float, retention: float) -> float:
    rate = BASE_RATES.get(industry, 0.0020)
    premium = annual_revenue * rate * (limit / 1_000_000) * (1 + retention / limit)
    return round(premium * CARRIER_MULTIPLIER, 2)


@app.post("/quotes")
async def create_quote(body: dict):
    limit = body.get("limit", 0)
    retention = body.get("retention", 0)

    if limit not in SUPPORTED_LIMITS:
        return {
            "error": "incompatible option",
            "message": f"The requested limit of {limit} is not available.",
        }

    if retention not in SUPPORTED_RETENTIONS:
        return {
            "error": "incompatible option",
            "message": f"The requested retention of {retention} is not available.",
        }

    premium = _calculate_premium(
        body.get("annual_revenue", 0),
        body.get("industry", "technology"),
        limit,
        retention,
    )
    quote_id = f"ca-{uuid.uuid4().hex[:8]}"
    quotes_store[quote_id] = {"premium": premium, "limit": limit, "retention": retention}
    stats["quotes_issued"] += 1

    return {
        "quote_id": quote_id,
        "premium": premium,
        "limit": limit,
        "retention": retention,
    }


@app.get("/quoting_options")
async def get_quoting_options():
    return {
        "supported_limits": SUPPORTED_LIMITS,
        "supported_retentions": SUPPORTED_RETENTIONS,
    }


@app.post("/bind")
async def bind_quote(body: dict):
    quote_id = body.get("quote_id", "")
    if quote_id not in quotes_store:
        return {"error": "quote not found"}
    stats["binds_completed"] += 1
    return {"status": "bound", "quote_id": quote_id}


@app.get("/status")
async def status():
    return {
        "carrier": "carrier_a",
        "status": "running",
        "quotes_issued": stats["quotes_issued"],
        "binds_completed": stats["binds_completed"],
    }
