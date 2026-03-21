from datetime import UTC, datetime

from app.schemas.exam import NormalizedExam
from app.services.hasher import hash_exam


def make_exam(title: str) -> NormalizedExam:
    return NormalizedExam(
        id="abc123",
        codice="CODE",
        titolo=title,
        descrizione="Desc",
        figura_ricercata="Role",
        settore="Tecnico e Progettazione",
        municipality="Rome",
        region="Lazio",
        province="Roma",
        data_pubblicazione=datetime(2025, 8, 4, 11, 15, tzinfo=UTC),
        data_scadenza=datetime(2025, 9, 4, 10, 0, tzinfo=UTC),
        tipo_procedura="ESAMI",
        selection_criteria=["Esami"],
        num_posti=2,
        salary_min=None,
        salary_max=None,
        salary_range=None,
        url="https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id=abc123",
        short_title="Role (2 posti), Rome",
        short_description="Desc",
        )

def test_hash_exam_is_deterministic():
    exam = make_exam("Title")
    assert hash_exam(exam) == hash_exam(exam)


def test_hash_exam_changes_when_content_changes():
    exam_a = make_exam("Title A")
    exam_b = make_exam("Title B")
    assert hash_exam(exam_a) != hash_exam(exam_b)


def test_hash_exam_changes_when_municipality_changes():
    exam_a = make_exam("Title")
    exam_b = exam_a.model_copy(update={"municipality": "Milan"})
    assert hash_exam(exam_a) != hash_exam(exam_b)
