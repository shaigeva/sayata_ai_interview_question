"""Carrier A client — with /quoting_options discovery and fallback logic."""

import httpx

from sayata.carriers.base import CarrierClient
from sayata.models import BindResponse, Quote, Submission


class CarrierAClient(CarrierClient):
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    async def _get_quoting_options(self, client: httpx.AsyncClient) -> dict:
        """Fetch supported limits and retentions from the carrier."""
        response = await client.get(f"{self.base_url}/quoting_options")
        return response.json()

    def _find_fallback_limit(self, requested: float, supported: list[float]) -> float:
        """Limits round UP: find the smallest supported limit >= requested.
        If none exists, use the highest available (best effort)."""
        candidates = [v for v in supported if v >= requested]
        if candidates:
            return min(candidates)
        return max(supported)

    def _find_fallback_retention(self, requested: float, supported: list[float]) -> float:
        """Retentions round DOWN: find the largest supported retention <= requested.
        If none exists, use the lowest available (best effort)."""
        candidates = [v for v in supported if v <= requested]
        if candidates:
            return max(candidates)
        return min(supported)

    async def get_quote(self, submission: Submission) -> Quote | None:
        async with httpx.AsyncClient() as client:
            # First attempt with requested values
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
                if "error" not in data:
                    return Quote(
                        carrier="carrier_a",
                        premium=int(data["premium"]),
                        limit=data["limit"],
                        retention=data["retention"],
                        quote_id=data["quote_id"],
                    )

            # Got an error — try fallback using quoting options
            try:
                options = await self._get_quoting_options(client)
                fallback_limit = self._find_fallback_limit(
                    submission.requested_limit, options["supported_limits"]
                )
                fallback_retention = self._find_fallback_retention(
                    submission.requested_retention, options["supported_retentions"]
                )

                response = await client.post(
                    f"{self.base_url}/quotes",
                    json={
                        "business_name": submission.business_name,
                        "industry": submission.industry,
                        "annual_revenue": submission.annual_revenue,
                        "limit": fallback_limit,
                        "retention": fallback_retention,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    if "error" not in data:
                        return Quote(
                            carrier="carrier_a",
                            premium=int(data["premium"]),
                            limit=data["limit"],
                            retention=data["retention"],
                            quote_id=data["quote_id"],
                        )
            except Exception:
                pass

            return None

    async def bind_quote(self, quote_id: str) -> BindResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/bind",
                json={"quote_id": quote_id},
            )
            data = response.json()
            return BindResponse(status=data["status"], quote_id=data["quote_id"], carrier="carrier_a")
