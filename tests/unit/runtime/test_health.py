from fastapi.testclient import TestClient

from aire_archeotech.runtime.app import app


def test_health_endpoint_is_stable_and_database_free() -> None:
    response = TestClient(app).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "service": "aire-archeotech-hunter",
        "status": "ok",
        "version": "0.1.0",
    }
