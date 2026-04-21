from decimal import Decimal

from app.services.normalizer import (
    ITALIAN_REGIONS,
    build_salary_range,
    build_short_title,
    clean_html_to_text,
    normalize_exam,
    parse_sedi,
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


# ---------------------------------------------------------------------------
# parse_sedi tests
# ---------------------------------------------------------------------------

def test_parse_sedi_empty():
    assert parse_sedi(None) == ([], [])
    assert parse_sedi([]) == ([], [])


def test_parse_sedi_single_region():
    regions, provinces = parse_sedi(["Lazio"])
    assert regions == ["Lazio"]
    assert provinces == []


def test_parse_sedi_region_and_province():
    regions, provinces = parse_sedi(["Lazio", "Roma"])
    assert regions == ["Lazio"]
    assert provinces == ["Roma"]


def test_parse_sedi_multiple_regions_only():
    """Case from the bug report — all entries are regions."""
    regions, provinces = parse_sedi(["Molise", "Abruzzo", "Marche", "Umbria"])
    assert regions == ["Molise", "Abruzzo", "Marche", "Umbria"]
    assert provinces == []


def test_parse_sedi_many_regions():
    """13 regions, none are provinces."""
    sedi = [
        "Lombardia", "Marche", "Umbria", "Piemonte", "Abruzzo",
        "Puglia", "Emilia Romagna", "Sicilia", "Liguria", "Veneto",
        "Lazio", "Toscana", "Campania",
    ]
    regions, provinces = parse_sedi(sedi)
    assert len(regions) == 13
    assert provinces == []
    for s in sedi:
        assert s in regions


def test_parse_sedi_mixed_regions_and_provinces():
    """Mix of regions and non-region locations."""
    regions, provinces = parse_sedi(["Lazio", "Roma", "Torino"])
    assert regions == ["Lazio"]
    assert provinces == ["Roma", "Torino"]


def test_italian_regions_set_has_20():
    assert len(ITALIAN_REGIONS) == 20


# ---------------------------------------------------------------------------
# normalize_exam — integration
# ---------------------------------------------------------------------------

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
    assert normalized.regions == ["Lazio"]
    assert normalized.provinces == ["Roma"]
    assert normalized.url.endswith("concorso_id=abc123")
    assert normalized.selection_criteria == ["Titoli", "Colloquio"]
    assert normalized.salary_range == "€24,000 - €32,000"


def test_normalize_exam_multi_region():
    """Multi-region exam should have all regions, no provinces."""
    raw_exam = {
        "id": "multi_region",
        "codice": "CODE",
        "titolo": "Concorso multi-regione",
        "descrizione": "<p>Desc</p>",
        "figuraRicercata": "Docente",
        "numPosti": 68,
        "dataPubblicazione": "2026-03-27T11:01:00Z",
        "dataScadenza": "2026-04-17T10:01:00Z",
        "tipoProcedura": "TITOLI_ESAMI",
        "salaryMin": None,
        "salaryMax": None,
        "entiRiferimento": ["Ministero dell'Istruzione"],
        "sedi": ["Molise", "Abruzzo", "Marche", "Umbria"],
    }

    normalized = normalize_exam(raw_exam)

    assert normalized.regions == ["Molise", "Abruzzo", "Marche", "Umbria"]
    assert normalized.provinces == []


def test_normalize_exam_no_sedi():
    raw_exam = {
        "id": "no_sedi",
        "codice": "CODE",
        "titolo": "Concorso senza sedi",
        "descrizione": "<p>Desc</p>",
        "figuraRicercata": "Funzionario",
        "numPosti": 1,
        "dataPubblicazione": "2026-01-01T00:00:00Z",
        "dataScadenza": None,
        "tipoProcedura": None,
        "salaryMin": None,
        "salaryMax": None,
        "entiRiferimento": [],
        "sedi": [],
    }

    normalized = normalize_exam(raw_exam)

    assert normalized.regions == []
    assert normalized.provinces == []


def test_clean_figura_ricercata():
    from app.services.normalizer import clean_figura_ricercata
    
    # Title casing
    assert clean_figura_ricercata("Istruttore amministrativo") == "Istruttore Amministrativo"
    
    # Acronym preservation
    assert clean_figura_ricercata("OSS - Operatore Socio Sanitario") == "OSS - Operatore Socio Sanitario"
    assert clean_figura_ricercata("CCNL del Comparto") == "CCNL Del Comparto"
    
    # All caps fallback
    assert clean_figura_ricercata("FUNZIONARIO TECNICO") == "Funzionario Tecnico"
    assert clean_figura_ricercata("ISTRUTTORE DIRETTIVO TECNICO ALTA SPECIALZZAZIONE") == "Istruttore Direttivo Tecnico Alta Specialzzazione"
    
    # Mixed with acronyms
    assert clean_figura_ricercata("Dirigente Medico M.E.U.") == "Dirigente Medico M.E.U."
    
    # Extra whitespace
    assert clean_figura_ricercata("  Operatore   Esperto  ") == "Operatore Esperto"
    
    # Long strings truncation
    long_string = "n. 1 incarico di collaborazione per lo svolgimento di attività di orientamento e supporto personalizzato a favore di studenti e studentesse con bisogni educativi speciali nell'ambito del Progetto NOI (Nuove opportunità inclusive)"
    cleaned_long = clean_figura_ricercata(long_string)
    assert len(cleaned_long) <= 100
    assert cleaned_long.endswith("...")
    assert "N. 1 Incarico Di Collaborazione" in cleaned_long
