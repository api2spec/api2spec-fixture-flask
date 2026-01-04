"""pytest fixtures."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.store import store


@pytest.fixture
def app() -> Flask:
    """Create test application."""
    app = create_app()
    app.config["TESTING"] = True

    # Clear store before each test
    store.clear()

    yield app

    # Clear store after each test
    store.clear()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client."""
    return app.test_client()
