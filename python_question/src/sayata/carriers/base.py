"""Base carrier client interface."""

from abc import ABC, abstractmethod

from sayata.models import BindResponse, Quote, Submission


class CarrierClient(ABC):
    """Abstract base class for carrier API clients."""

    @abstractmethod
    async def get_quote(self, submission: Submission) -> Quote | None:
        """Request a quote from the carrier. Returns None if quoting fails."""
        ...

    @abstractmethod
    async def bind_quote(self, quote_id: str) -> BindResponse:
        """Send a bind request to the carrier."""
        ...
