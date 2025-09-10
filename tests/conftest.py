"""Pytest configuration for API integration tests."""

import os
import pytest
from fastapi.testclient import TestClient


os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_INMEM_DB"] = "true"

from app.main import app 


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Yield a TestClient for interacting with the FastAPI app."""
    return TestClient(app)