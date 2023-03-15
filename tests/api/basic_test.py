from fastapi.testclient import TestClient
from app.api_main import app
from app.dependencies import get_dw_cursor


def override_get_dw_cursor():
    return False


app.dependency_overrides[get_dw_cursor] = override_get_dw_cursor


def test_heartbeat():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
