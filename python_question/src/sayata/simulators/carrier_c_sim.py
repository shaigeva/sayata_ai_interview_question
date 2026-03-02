"""Carrier C simulator — polling-based quotes.

POST /quotes returns 202 with a quote_id and status "pending".
The quote becomes "ready" after a short delay. Callers must poll
GET /quotes/{quote_id} to retrieve the final quote.
"""

import asyncio
import uuid

from fastapi import FastAPI

app = FastAPI(title="Carrier C Simulator")

QUOTE_DELAY_SECONDS = 3

BASE_RATES = {
    "technology": 0.0016,
    "manufacturing": 0.0022,
    "retail": 0.0018,
    "healthcare": 0.0025,
    "finance": 0.0020,
}
CARRIER_MULTIPLIER = 1.1

quotes_store: dict[str, dict] = {}
stats = {"quotes_issued": 0, "binds_completed": 0}


def _calculate_premium(annual_revenue: float, industry: str, limit: float, retention: float) -> float:
    rate = BASE_RATES.get(industry, 0.0020)
    premium = annual_revenue * rate * (limit / 1_000_000) * (1 + retention / limit)
    return round(premium * CARRIER_MULTIPLIER, 2)


async def _finalize_quote(quote_id: str, annual_revenue: float, industry: str, limit: float, retention: float):
    await asyncio.sleep(QUOTE_DELAY_SECONDS)
    premium = _calculate_premium(annual_revenue, industry, limit, retention)
    quotes_store[quote_id].update({
        "status": "ready",
        "premium": premium,
    })
    stats["quotes_issued"] += 1


@app.post("/quotes", status_code=202)
async def create_quote(body: dict):
    limit = body.get("limit", 1_000_000)
    retention = body.get("retention", 50_000)

    quote_id = f"cc-{uuid.uuid4().hex[:8]}"
    quotes_store[quote_id] = {
        "quote_id": quote_id,
        "status": "pending",
        "limit": limit,
        "retention": retention,
    }

    asyncio.create_task(
        _finalize_quote(
            quote_id,
            body.get("annual_revenue", 0),
            body.get("industry", "technology"),
            limit,
            retention,
        )
    )

    return {
        "quote_id": quote_id,
        "status": "pending",
        "poll_url": f"/quotes/{quote_id}",
    }


@app.get("/quotes/{quote_id}")
async def get_quote(quote_id: str):
    quote = quotes_store.get(quote_id)
    if quote is None:
        return {"error": "quote not found"}

    if quote["status"] == "pending":
        return {"quote_id": quote_id, "status": "pending"}

    return {
        "quote_id": quote_id,
        "status": "ready",
        "premium": quote["premium"],
        "limit": quote["limit"],
        "retention": quote["retention"],
    }


@app.post("/bind")
async def bind_quote(body: dict):
    quote_id = body.get("quote_id", "")
    quote = quotes_store.get(quote_id)
    if quote is None:
        return {"error": "quote not found"}
    if quote["status"] != "ready":
        return {"error": "quote not ready"}
    stats["binds_completed"] += 1
    return {"status": "bound", "quote_id": quote_id}


@app.get("/status")
async def status():
    return {
        "carrier": "carrier_c",
        "status": "running",
        "quotes_issued": stats["quotes_issued"],
        "binds_completed": stats["binds_completed"],
    }
