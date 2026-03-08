from decimal import Decimal

from app.services.normalizer import (
    build_salary_range,
    build_short_title,
    clean_html_to_text,
    normalize_exam,
    simplify_selection_criteria,
)


def test_clean_html_to_text_strips_tags_and_entities():
    raw = '<p><strong>Hello&nbsp;World</strong> <span>INPA</span></p>'
    cleaned = clean_html_to_text(raw)
    assert cleaned == "Hello World INPA"


def test_build_short_title_graceful_partial():
    assert build_short_title("Istruttore", 2, "Roma") == "Istruttore (2 posti), Roma"
    assert build_short_title("Istruttore", None, "Roma") == "Istruttore, Roma"
    assert build_short_title(None, 2, None) == "Concorso (2 posti)"


def test_build_salary_range_variants():
    assert build_salary_range(Decimal("24000"), Decimal("32000")) == "€24,000 - €32,000"
    assert build_salary_range(Decimal("24000"), None) == "Da €24,000"
    assert build_salary_range(None, Decimal("32000")) == "Fino a €32,000"
    assert build_salary_range(None, None) is None


def test_simplify_selection_criteria_maps_technical_value():
    assert simplify_selection_criteria("TITOLI_COLLOQUIO") == ["Titoli", "Colloquio"]
    assert simplify_selection_criteria("ESAMI_SOMETHING") == ["Esami", "Altro"]
    assert simplify_selection_criteria(None) == []


def test_normalize_exam_maps_location_url_and_simplified_fields():
    raw_exam = {
        "id": "abc123",
        "codice": "CODE",
        "titolo": "Concorso test",
        "descrizione": "<p>Descrizione</p>",
        "figuraRicercata": "Istruttore",
        "numPosti": 2,
        "dataPubblicazione": "2025-08-04T11:15:00Z",
        "dataScadenza": "2025-09-04T10:00:00Z",
        "tipoProcedura": "TITOLI_COLLOQUIO",
        "salaryMin": 24000,
        "salaryMax": 32000,
        "entiRiferimento": ["Roma"],
        "sedi": ["Lazio", "Roma"],
    }

    normalized = normalize_exam(raw_exam)

    assert normalized.municipality == "Roma"
    assert normalized.region == "Lazio"
    assert normalized.province == "Roma"
    assert normalized.url.endswith("concorso_id=abc123")
    assert normalized.selection_criteria == ["Titoli", "Colloquio"]
    assert normalized.salary_range == "€24,000 - €32,000"
