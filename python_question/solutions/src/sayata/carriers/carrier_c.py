"""Carrier C client — async polling pattern."""

import asyncio

import httpx

from sayata.carriers.base import CarrierClient
from sayata.models import BindResponse, Quote, Submission

POLL_INTERVAL = 1  # seconds between polls
POLL_TIMEOUT = 30  # max seconds to wait


class CarrierCClient(CarrierClient):
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url

    async def get_quote(self, submission: Submission) -> Quote | None:
        async with httpx.AsyncClient() as client:
            # POST /quotes returns 202 with a poll_url
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
            if response.status_code != 202:
                return None

            data = response.json()
            quote_id = data["quote_id"]
            poll_url = f"{self.base_url}/quotes/{quote_id}"

            # Poll until ready or timeout
            elapsed = 0
            while elapsed < POLL_TIMEOUT:
                await asyncio.sleep(POLL_INTERVAL)
                elapsed += POLL_INTERVAL

                poll_resp = await client.get(poll_url)
                poll_data = poll_resp.json()

                if poll_data.get("status") == "ready":
                    return Quote(
                        carrier="carrier_c",
                        premium=int(poll_data["premium"]),
                        limit=poll_data["limit"],
                        retention=poll_data["retention"],
                        quote_id=poll_data["quote_id"],
                    )

            return None

    async def bind_quote(self, quote_id: str) -> BindResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/bind",
                json={"quote_id": quote_id},
            )
            data = response.json()
            return BindResponse(status=data["status"], quote_id=data["quote_id"], carrier="carrier_c")
