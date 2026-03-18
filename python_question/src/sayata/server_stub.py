"""Sayata quoting platform — stub server.

This is a placeholder that verifies your environment can run a FastAPI server.
It will be replaced with the full implementation during the interview.
"""

from fastapi import FastAPI

app = FastAPI(title="Sayata Quoting Platform")


@app.get("/health")
async def health():
    return {"status": "ok"}
