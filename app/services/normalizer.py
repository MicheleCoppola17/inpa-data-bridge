import html
import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from bs4 import BeautifulSoup

from app.schemas.exam import NormalizedExam

_WHITESPACE_RE = re.compile(r"\s+")


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
    sede: str | None,
) -> str:
    figura = (figura_ricercata or "").strip() or "Concorso"
    posti = f" ({num_posti})" if num_posti is not None else ""
    sede_clean = (sede or "").strip()
    luogo = f", {sede_clean}" if sede_clean else ""
    return f"{figura}{posti}{luogo}"


def normalize_exam(raw_exam: dict[str, Any]) -> NormalizedExam:
    enti = raw_exam.get("entiRiferimento")
    sede_estratta = enti[0] if enti and len(enti) > 0 else None
    figura_ricercata = raw_exam.get("figuraRicercata")
    num_posti = raw_exam.get("numPosti")
    return NormalizedExam(
        id=str(raw_exam["id"]),
        codice=str(raw_exam.get("codice") or ""),
        titolo=str(raw_exam.get("titolo") or ""),
        descrizione=clean_html_to_text(raw_exam.get("descrizione")),
        sede=sede_estratta,
        figura_ricercata=figura_ricercata,
        num_posti=num_posti,
        data_pubblicazione=parse_iso_datetime(raw_exam.get("dataPubblicazione")),
        data_scadenza=parse_iso_datetime(raw_exam.get("dataScadenza")),
        tipo_procedura=raw_exam.get("tipoProcedura"),
        salary_min=Decimal(str(raw_exam["salaryMin"])) if raw_exam.get("salaryMin") is not None else None,
        salary_max=Decimal(str(raw_exam["salaryMax"])) if raw_exam.get("salaryMax") is not None else None,
        short_title=build_short_title(figura_ricercata, num_posti, sede_estratta),
    )
