from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_general_health_check() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == "portfolio-api"
    assert payload["environment"] == "local"
    assert "timestamp" in payload


def test_liveness_check() -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == "portfolio-api"


def test_cors_allows_frontend_origin() -> None:
    response = client.options(
        "/api/v1/portfolio/projects",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_rejects_unapproved_origin() -> None:
    response = client.options(
        "/api/v1/portfolio/projects",
        headers={
            "Origin": "http://malicious.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers
