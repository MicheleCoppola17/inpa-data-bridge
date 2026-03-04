from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_health_check_ok(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()

    async def mock_db_ping() -> bool:
        return True

    monkeypatch.setattr("app.api.v1.endpoints.health.db_ping", mock_db_ping)

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["db"] == "up"


def test_health_check_db_down(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()

    async def mock_db_ping() -> bool:
        return False

    monkeypatch.setattr("app.api.v1.endpoints.health.db_ping", mock_db_ping)

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["db"] == "down"
