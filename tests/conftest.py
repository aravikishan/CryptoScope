"""Shared pytest fixtures for CryptoScope tests."""

import sys
import os
import pytest

# Ensure project root is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app  # noqa: E402
from models.database import db as _db  # noqa: E402


@pytest.fixture(scope="session")
def app():
    """Create an application instance for testing."""
    application = create_app(testing=True)
    yield application


@pytest.fixture(scope="session")
def _setup_db(app):
    """Create tables once per session."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture()
def db_session(app, _setup_db):
    """Per-test database session with rollback."""
    with app.app_context():
        connection = _setup_db.engine.connect()
        transaction = connection.begin()
        session = _setup_db.session
        yield session
        session.rollback()
        transaction.close()
        connection.close()


@pytest.fixture()
def client(app):
    """Flask test client."""
    with app.test_client() as c:
        with app.app_context():
            yield c
