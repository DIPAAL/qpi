from fastapi.testclient import TestClient
from app.main_api import app


def test_heartbeat():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

