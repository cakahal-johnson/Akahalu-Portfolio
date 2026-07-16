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
