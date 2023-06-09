from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.api_main import app
from app.dependencies import get_dw


def test_heartbeat_pass():
    cursor_mock = MagicMock()
    cursor_mock.fetchone.return_value = (1,)

    def override_get_dw():
        return cursor_mock

    app.dependency_overrides[get_dw()] = override_get_dw

    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"message": "Data warehouse is accessible."}
