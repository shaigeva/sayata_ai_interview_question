"""Setup verification — proves the environment is working."""

from fastapi.testclient import TestClient

from sayata.server import app


def test_imports():
    """Verify key dependencies are installed."""
    import httpx  # noqa: F401
    import pydantic  # noqa: F401
    import requests  # noqa: F401
    import uvicorn  # noqa: F401


def test_server_health():
    """Verify the server starts and responds."""
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
