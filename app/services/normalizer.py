import html
import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from bs4 import BeautifulSoup

from app.schemas.exam import NormalizedExam

_WHITESPACE_RE = re.compile(r"\s+")
_SPLIT_NON_ALNUM_RE = re.compile(r"[^A-Z0-9]+")
_SELECTION_CRITERIA_MAP = {
    "COLLOQUIO": "Colloquio",
    "ESAME": "Esami",
    "ESAMI": "Esami",
    "TITOLO": "Titoli",
    "TITOLI": "Titoli",
}
_EXAM_DETAIL_BASE_URL = (
    "https://www.inpa.gov.it/bandi-e-avvisi/dettaglio-bando-avviso/?concorso_id="
)


def clean_html_to_text(value: str | None) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = html.unescape(text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def build_short_title(
    figura_ricercata: str | None,
    num_posti: int | None,
    municipality: str | None,
) -> str:
    figura = (figura_ricercata or "").strip() or "Concorso"
    if num_posti is None:
        posti = ""
    elif num_posti == 1:
        posti = f" ({num_posti} posto)"
    else:
        posti = f" ({num_posti} posti)"
    municipality_clean = (municipality or "").strip()
    luogo = f", {municipality_clean}" if municipality_clean else ""
    return f"{figura}{posti}{luogo}"


def format_eur_amount(amount: Decimal) -> str:
    if amount == amount.to_integral_value():
        return f"€{int(amount):,}"
    return f"€{amount:,.2f}"


def build_salary_range(salary_min: Decimal | None, salary_max: Decimal | None) -> str | None:
    if salary_min is not None and salary_max is not None:
        return f"{format_eur_amount(salary_min)} - {format_eur_amount(salary_max)}"
    if salary_min is not None:
        return f"Da {format_eur_amount(salary_min)}"
    if salary_max is not None:
        return f"Fino a {format_eur_amount(salary_max)}"
    return None


def simplify_selection_criteria(tipo_procedura: str | None) -> list[str]:
    if not tipo_procedura:
        return []

    criteria: list[str] = []
    has_unknown = False
    tokens = [token for token in _SPLIT_NON_ALNUM_RE.split(tipo_procedura.upper()) if token]
    for token in tokens:
        mapped = _SELECTION_CRITERIA_MAP.get(token)
        if mapped and mapped not in criteria:
            criteria.append(mapped)
        elif mapped is None:
            has_unknown = True

    if has_unknown and "Altro" not in criteria:
        criteria.append("Altro")

    return criteria


def normalize_exam(raw_exam: dict[str, Any]) -> NormalizedExam:
    enti = raw_exam.get("entiRiferimento")
    municipality = enti[0] if enti and len(enti) > 0 else None
    sedi = raw_exam.get("sedi")
    region = sedi[0] if sedi and len(sedi) > 0 else None
    province = sedi[1] if sedi and len(sedi) > 1 else None
    figura_ricercata = raw_exam.get("figuraRicercata")
    num_posti = raw_exam.get("numPosti")
    tipo_procedura = raw_exam.get("tipoProcedura")
    salary_min = Decimal(str(raw_exam["salaryMin"])) if raw_exam.get("salaryMin") is not None else None
    salary_max = Decimal(str(raw_exam["salaryMax"])) if raw_exam.get("salaryMax") is not None else None
    exam_id = str(raw_exam["id"])

    return NormalizedExam(
        id=exam_id,
        codice=str(raw_exam.get("codice") or ""),
        titolo=str(raw_exam.get("titolo") or ""),
        descrizione=clean_html_to_text(raw_exam.get("descrizione")),
        municipality=municipality,
        region=region,
        province=province,
        figura_ricercata=figura_ricercata,
        num_posti=num_posti,
        data_pubblicazione=parse_iso_datetime(raw_exam.get("dataPubblicazione")),
        data_scadenza=parse_iso_datetime(raw_exam.get("dataScadenza")),
        tipo_procedura=tipo_procedura,
        selection_criteria=simplify_selection_criteria(tipo_procedura),
        salary_min=salary_min,
        salary_max=salary_max,
        salary_range=build_salary_range(salary_min, salary_max),
        url=f"{_EXAM_DETAIL_BASE_URL}{exam_id}",
        short_title=build_short_title(figura_ricercata, num_posti, municipality),
    )
