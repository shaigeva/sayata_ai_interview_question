import os

import pytest

BASE_PORT = int(os.environ.get("BASE_PORT", "8000"))


@pytest.fixture
def base_url():
    return f"http://localhost:{BASE_PORT}"
