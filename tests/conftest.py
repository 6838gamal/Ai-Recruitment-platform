"""
Pytest configuration and fixtures.
All test modules can import fixtures from here.
"""
import os
import pytest
from typing import Generator

# Use a separate test database
os.environ.setdefault("DATABASE_URL", os.environ.get("DATABASE_URL", "postgresql://localhost/ai_recruitment_test"))
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-not-secure")


@pytest.fixture(scope="session")
def test_settings():
    """Return test settings."""
    from app.config import settings
    return settings


@pytest.fixture(scope="function")
def mock_db():
    """Mock database session for unit tests."""
    from unittest.mock import MagicMock
    return MagicMock()
