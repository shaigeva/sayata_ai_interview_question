"""Sayata quoting platform — stub server.

This is a placeholder that verifies your environment can run a FastAPI server
with Pydantic models. It will be replaced with the full implementation during
the interview.
"""

from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str = "sayata"


app = FastAPI(title="Sayata Quoting Platform")


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")
