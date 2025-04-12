import os
import pytest
from pyscrum.database import init_db

@pytest.fixture(autouse=True)
def setup_test_db():
    """Setup a fresh test database for each test."""
    if os.path.exists("pyscrum.db"):
        os.remove("pyscrum.db")
    init_db()
    yield
    if os.path.exists("pyscrum.db"):
        os.remove("pyscrum.db")