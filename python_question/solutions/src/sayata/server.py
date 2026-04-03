"""Sayata quoting platform — reference solution with all 4 carriers."""

import asyncio
import os
import uuid

from fastapi import FastAPI, HTTPException

from sayata.carriers.carrier_a import CarrierAClient
from sayata.carriers.carrier_b import CarrierBClient
from sayata.carriers.carrier_c import CarrierCClient
from sayata.carriers.carrier_d import CarrierDClient
from sayata.models import (
    BindRequest,
    BindResponse,
    Quote,
    Submission,
    SubmissionCreate,
    SubmissionDetail,
    SubmissionResponse,
)

app = FastAPI(title="Sayata Quoting Platform")

BASE_PORT = int(os.environ.get("BASE_PORT", "8000"))


@app.get("/health")
async def health():
    return {"status": "ok"}


# In-memory state
submissions: dict[str, Submission] = {}
submission_quotes: dict[str, list[Quote]] = {}

# Registered carriers — all 4 wired in.
CARRIERS = [
    CarrierAClient(base_url=f"http://localhost:{BASE_PORT + 1}"),
    CarrierBClient(base_url=f"http://localhost:{BASE_PORT + 2}"),
    CarrierCClient(base_url=f"http://localhost:{BASE_PORT + 3}"),
    CarrierDClient(base_url=f"http://localhost:{BASE_PORT + 4}"),
]

# Map carrier names to clients for bind routing
CARRIER_MAP = {
    "carrier_a": CARRIERS[0],
    "carrier_b": CARRIERS[1],
    "carrier_c": CARRIERS[2],
    "carrier_d": CARRIERS[3],
}


@app.post("/submissions", response_model=SubmissionResponse, status_code=201)
async def create_submission(body: SubmissionCreate):
    submission_id = str(uuid.uuid4())
    submission = Submission(id=submission_id, **body.model_dump())

    # Fetch quotes from all registered carriers concurrently
    async def safe_get_quote(carrier):
        try:
            return await carrier.get_quote(submission)
        except Exception:
            return None

    results = await asyncio.gather(*(safe_get_quote(c) for c in CARRIERS))
    quotes = [q for q in results if q is not None]

    submission.status = "quoted"
    submissions[submission_id] = submission
    submission_quotes[submission_id] = quotes

    return SubmissionResponse(id=submission_id, status=submission.status)


@app.get("/submissions/{submission_id}", response_model=SubmissionDetail)
async def get_submission(submission_id: str):
    submission = submissions.get(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    quotes = submission_quotes.get(submission_id, [])
    return SubmissionDetail(
        id=submission.id,
        business_name=submission.business_name,
        industry=submission.industry,
        annual_revenue=submission.annual_revenue,
        requested_limit=submission.requested_limit,
        requested_retention=submission.requested_retention,
        status=submission.status,
        quotes=quotes,
    )


@app.post("/submissions/{submission_id}/bind", response_model=BindResponse)
async def bind_submission(submission_id: str, body: BindRequest):
    submission = submissions.get(submission_id)
    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    quotes = submission_quotes.get(submission_id, [])
    matching = [q for q in quotes if q.quote_id == body.quote_id and q.carrier == body.carrier]
    if not matching:
        raise HTTPException(status_code=404, detail="Quote not found for this submission")

    carrier_client = CARRIER_MAP.get(body.carrier)
    if carrier_client is None:
        raise HTTPException(status_code=400, detail="Unknown carrier")

    return await carrier_client.bind_quote(body.quote_id)
