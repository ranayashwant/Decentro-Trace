import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.main import app
from app.core.database import init_db
from app.seed.loader import load_seed_files


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Setup test database and seed data
    init_db()
    seed_dir = backend_path.parent / "seed"
    load_seed_files(str(seed_dir))
    yield


@pytest.fixture
def client():
    return TestClient(app)
