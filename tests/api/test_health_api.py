from flask.testing import FlaskClient
import pytest

pytestmark = pytest.mark.api

def test_health_api(
    api_client: FlaskClient,
) -> None:
    response = api_client.get("/health")

    assert response.status_code == 200

    body = response.get_json()

    assert body is not None
    assert body["status"] == "SUCCESS"
    assert body["message"] == "API is healthy"
    assert body["data"]["state"] == "UP"
    assert body["data"]["service"] == (
        "enterprise-ecommerce-api"
    )


def test_readiness_api(
    api_client: FlaskClient,
) -> None:
    response = api_client.get("/ready")

    assert response.status_code == 200

    body = response.get_json()

    assert body is not None
    assert body["status"] == "SUCCESS"
    assert body["data"]["ready"] is True


def test_version_api(
    api_client: FlaskClient,
) -> None:
    response = api_client.get("/api/version")

    assert response.status_code == 200

    body = response.get_json()

    assert body is not None
    assert body["status"] == "SUCCESS"
    assert body["data"]["api_version"] == "v1"
    assert body["data"]["framework_version"] == "1.0.0"


def test_unknown_api_returns_404(
    api_client: FlaskClient,
) -> None:
    response = api_client.get(
        "/api/v1/unknown-resource"
    )

    assert response.status_code == 404

    body = response.get_json()

    assert body is not None
    assert body["status"] == "ERROR"
    assert body["message"] == (
        "Requested API resource was not found"
    )


def test_invalid_http_method_returns_405(
    api_client: FlaskClient,
) -> None:
    response = api_client.post("/health")

    assert response.status_code == 405

    body = response.get_json()

    assert body is not None
    assert body["status"] == "ERROR"
    assert body["message"] == (
        "HTTP method is not allowed for this resource"
    )