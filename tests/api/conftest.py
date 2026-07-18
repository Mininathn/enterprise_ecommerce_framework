import pytest
from flask import Flask
from flask.testing import FlaskClient

from api.app import create_app


@pytest.fixture(scope="session")
def api_app() -> Flask:
    """Create the Flask application for API testing."""

    app = create_app(testing=True)

    return app


@pytest.fixture()
def api_client(
    api_app: Flask,
) -> FlaskClient:
    """Return a Flask test client."""

    return api_app.test_client()