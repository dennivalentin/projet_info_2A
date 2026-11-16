"""Shared pytest configuration for the backend tests."""

import os

import pytest

from utils.env_variables import load_environment_variables

load_environment_variables()

os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_only_for_pytest_0123456789")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

# The tests must never touch the application data: every connection opened
# during the tests uses the dedicated test schema
os.environ["POSTGRES_SCHEMA"] = "project_test_dao"


@pytest.fixture(scope="session")
def test_database():
    """Re-creates the test schema with data/pop_db_test.sql (once per test session).

    Tests that need a real PostgreSQL database use this fixture. They are
    skipped, instead of failing, when no database is configured or reachable.
    """
    from dao.db_connection import DBConnection
    from utils.reset_database import ResetDatabase

    try:
        _ = DBConnection().connection  # opens the connection, or raises
    except Exception as e:
        pytest.skip(f"PostgreSQL not available: {e}")

    ResetDatabase().run(test_dao=True)
