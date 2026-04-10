from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.deps import get_session
from app.core.config import get_settings
from app.main import create_app


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class FakeSession:
    def __init__(self, exam):
        self._exam = exam

    async def scalars(self, _query):
        return FakeScalarResult([self._exam])

    async def scalar(self, _query):
        return 1

    async def get(self, _model, exam_id):
        if exam_id == self._exam.id:
            return self._exam
        return None


exam_fixture = SimpleNamespace(
    id="abc123",
    codice="UF6Y8Q_3_2025",
    titolo="Concorso test",
    descrizione="Descrizione",
    figura_ricercata="Istruttore",
    settore="Amministrativo e Contabile",
    data_pubblicazione=datetime(2025, 8, 4, 11, 15, tzinfo=UTC),
    data_scadenza=datetime(2025, 9, 4, 10, 0, tzinfo=UTC),
    tipo_procedura="ESAMI",
    selection_criteria=["Esami"],
    num_posti=2,
    salary_min=None,
    salary_max=None,
    salary_range=None,
    municipality="Roma",
    region="Lazio",
    province="Roma",
    url="https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=abc123",
    short_title="Istruttore (2 posti), Roma",
    short_description="Descrizione",
    content_hash="a" * 64,
    first_seen_at=datetime(2025, 8, 4, 11, 15, tzinfo=UTC),
    last_seen_at=datetime(2025, 8, 4, 11, 15, tzinfo=UTC),
    updated_at=datetime(2025, 8, 4, 11, 15, tzinfo=UTC),
    is_expired=False,
)


async def override_session():
    yield FakeSession(exam_fixture)


def test_list_exams(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        response = client.get("/api/v1/exams")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["short_title"] == "Istruttore (2 posti), Roma"
    assert item["organization"] == "Roma"
    assert item["sector"] == "Amministrativo e Contabile"
    assert item["url"].endswith("concorso_id=abc123")
    assert "published_at" in item
    assert "codice" not in item
    assert "titolo" not in item


def test_list_exams_filter_sector(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        # Correct sector
        response = client.get("/api/v1/exams?sector=Amministrativo e Contabile")
        assert response.status_code == 200
        assert len(response.json()["items"]) == 1

        # Wrong sector
        response = client.get("/api/v1/exams?sector=Wrong")
        assert response.status_code == 200


def test_get_exam(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        response = client.get("/api/v1/exams/abc123")

    assert response.status_code == 200
    assert response.json()["id"] == "abc123"
    assert response.json()["short_title"] == "Istruttore (2 posti), Roma"
    assert response.json()["selection_criteria"] == ["Esami"]


def test_get_exam_not_found(monkeypatch):
    monkeypatch.setenv("SYNC_ENABLED", "false")
    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_session] = override_session

    with TestClient(app) as client:
        response = client.get("/api/v1/exams/missing")

    assert response.status_code == 404
