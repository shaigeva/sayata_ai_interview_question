"""Carrier B simulator — synchronous quotes with comma-formatted prices.

Returns premiums as comma-formatted strings (e.g. "2,343" instead of 2343).
This causes parsing issues for naive int() calls when premium >= 1,000.
"""

import uuid

from fastapi import FastAPI

app = FastAPI(title="Carrier B Simulator", docs_url="/api_info", redoc_url=None, openapi_url="/api_info/openapi.json")

BASE_RATES = {
    "technology": 0.0016,
    "manufacturing": 0.0022,
    "retail": 0.0018,
    "healthcare": 0.0025,
    "finance": 0.0020,
}
CARRIER_MULTIPLIER = 0.95

quotes_store: dict[str, dict] = {}
stats = {"quotes_issued": 0, "binds_completed": 0}


def _calculate_premium(annual_revenue: float, industry: str, limit: float, retention: float) -> float:
    rate = BASE_RATES.get(industry, 0.0020)
    premium = annual_revenue * rate * (limit / 1_000_000) * (1 + retention / limit)
    return round(premium * CARRIER_MULTIPLIER, 2)


@app.post("/quotes")
async def create_quote(body: dict):
    limit = body.get("limit", 1_000_000)
    retention = body.get("retention", 50_000)

    premium = _calculate_premium(
        body.get("annual_revenue", 0),
        body.get("industry", "technology"),
        limit,
        retention,
    )

    quote_id = f"cb-{uuid.uuid4().hex[:8]}"
    quotes_store[quote_id] = {"premium": premium, "limit": limit, "retention": retention}
    stats["quotes_issued"] += 1

    # Return premium as a comma-formatted string for large values,
    # raw number for small values — inconsistent serialization.
    return {
        "quote_id": quote_id,
        "premium": f"{premium:,.0f}" if premium >= 1000 else premium,
        "limit": limit,
        "retention": retention,
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
        "carrier": "carrier_b",
        "status": "running",
        "quotes_issued": stats["quotes_issued"],
        "binds_completed": stats["binds_completed"],
    }
