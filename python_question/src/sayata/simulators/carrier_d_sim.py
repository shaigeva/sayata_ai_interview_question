"""Carrier D simulator — unfamiliar API shape.

Uses completely different endpoint paths and field names from the other carriers.
The /api/v1/info endpoint lists available endpoints as a discovery breadcrumb.
"""

import uuid

from fastapi import FastAPI

app = FastAPI(title="Carrier D Simulator")

BASE_RATES = {
    "technology": 0.0016,
    "manufacturing": 0.0022,
    "retail": 0.0018,
    "healthcare": 0.0025,
    "finance": 0.0020,
}
CARRIER_MULTIPLIER = 0.9

requests_store: dict[str, dict] = {}
stats = {"quotes_issued": 0, "binds_completed": 0}


def _calculate_premium(revenue: float, sector: str, coverage_amount: float, deductible: float) -> float:
    rate = BASE_RATES.get(sector, 0.0020)
    premium = revenue * rate * (coverage_amount / 1_000_000) * (1 + deductible / coverage_amount)
    return round(premium * CARRIER_MULTIPLIER, 2)


@app.post("/api/v1/insurance-request")
async def create_request(body: dict):
    coverage_amount = body.get("coverage_amount", 1_000_000)
    deductible = body.get("deductible", 50_000)

    annual_cost = _calculate_premium(
        body.get("revenue", 0),
        body.get("sector", "technology"),
        coverage_amount,
        deductible,
    )

    request_id = f"cd-{uuid.uuid4().hex[:8]}"
    requests_store[request_id] = {
        "annual_cost": annual_cost,
        "max_coverage": coverage_amount,
        "deductible_amount": deductible,
    }
    stats["quotes_issued"] += 1

    return {
        "request_id": request_id,
        "annual_cost": annual_cost,
        "max_coverage": coverage_amount,
        "deductible_amount": deductible,
        "provider": "carrier_d",
    }


@app.post("/api/v1/accept")
async def accept_request(body: dict):
    request_id = body.get("request_id", "")
    if request_id not in requests_store:
        return {"error": "request not found"}
    stats["binds_completed"] += 1
    return {"confirmation": "accepted", "request_id": request_id}


@app.get("/api/v1/info")
async def info():
    return {
        "service": "carrier_d",
        "version": "1.0",
        "endpoints": [
            {"method": "POST", "path": "/api/v1/insurance-request", "description": "Submit an insurance request"},
            {"method": "POST", "path": "/api/v1/accept", "description": "Accept an insurance quote"},
            {"method": "GET", "path": "/api/v1/info", "description": "Service information"},
        ],
    }
