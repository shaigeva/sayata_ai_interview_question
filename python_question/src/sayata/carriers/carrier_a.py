"""Carrier A client."""

import httpx

from sayata.carriers.base import CarrierClient
from sayata.models import BindResponse, Quote, Submission


class CarrierAClient(CarrierClient):
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    async def get_quote(self, submission: Submission) -> Quote | None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/quotes",
                json={
                    "business_name": submission.business_name,
                    "industry": submission.industry,
                    "annual_revenue": submission.annual_revenue,
                    "limit": submission.requested_limit,
                    "retention": submission.requested_retention,
                },
            )
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

    async def bind_quote(self, quote_id: str) -> BindResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/bind",
                json={"quote_id": quote_id},
            )
            data = response.json()
            return BindResponse(status=data["status"], quote_id=data["quote_id"], carrier="carrier_a")
