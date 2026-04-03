"""Carrier D client — different API shape with field mapping."""

import httpx

from sayata.carriers.base import CarrierClient
from sayata.models import BindResponse, Quote, Submission


class CarrierDClient(CarrierClient):
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url

    async def get_quote(self, submission: Submission) -> Quote | None:
        async with httpx.AsyncClient() as client:
            # Carrier D uses different field names:
            #   revenue (not annual_revenue)
            #   coverage_amount (not limit)
            #   deductible (not retention)
            response = await client.post(
                f"{self.base_url}/api/v1/insurance-request",
                json={
                    "business_name": submission.business_name,
                    "industry": submission.industry,
                    "revenue": submission.annual_revenue,
                    "coverage_amount": submission.requested_limit,
                    "deductible": submission.requested_retention,
                },
            )
            if response.status_code == 200:
                data = response.json()
                if "error" not in data:
                    # Map Carrier D fields back to standard format:
                    #   annual_cost -> premium
                    #   max_coverage -> limit
                    #   deductible_amount -> retention
                    #   request_id -> quote_id
                    return Quote(
                        carrier="carrier_d",
                        premium=int(data["annual_cost"]),
                        limit=data["max_coverage"],
                        retention=data["deductible_amount"],
                        quote_id=data["request_id"],
                    )
            return None

    async def bind_quote(self, quote_id: str) -> BindResponse:
        async with httpx.AsyncClient() as client:
            # Carrier D uses /api/v1/accept with request_id
            response = await client.post(
                f"{self.base_url}/api/v1/accept",
                json={"request_id": quote_id},
            )
            data = response.json()
            return BindResponse(
                status="bound" if data.get("confirmation") == "accepted" else data.get("status", "error"),
                quote_id=quote_id,
                carrier="carrier_d",
            )
