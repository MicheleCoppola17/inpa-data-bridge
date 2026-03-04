from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_sync_status(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/v1/internal/sync/status")

    assert response.status_code == 200
    payload = response.json()
    assert "running" in payload
    assert "scheduler_started" in payload


def test_trigger_sync_accepts(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()

    with TestClient(app) as client:
        response = client.post("/api/v1/internal/sync/run")

    assert response.status_code == 202
