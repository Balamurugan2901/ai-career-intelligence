import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.main import app
from backend.models.database import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initializes database schema for test suite."""
    init_db()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client
