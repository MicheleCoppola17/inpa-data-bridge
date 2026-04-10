import html
import re
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from bs4 import BeautifulSoup

from app.schemas.exam import NormalizedExam

_WHITESPACE_RE = re.compile(r"\s+")

# ---------------------------------------------------------------------------
# Settore classification
# ---------------------------------------------------------------------------

_SETTORE_KEYWORDS: list[tuple[str, list[str]]] = [
    (
        "Tecnico e Progettazione",
        [
            "tecnico", "tecniche", "tecnici", "ingegnere", "ingegneri", "architetto", "architetti", "geometra", "geometri", "tecnologo", "tecnologi",
            "progettazione", "urbanistica", "perito", "periti", "edilizia", "trasporti",
            "infrastrutture", "paesaggio", "monitoraggio",
        ],
    ),
    (
        "Ambiente e Territorio",
        [
            "agricoltura", "foreste", "cava", "bonifiche", "rifiuti",
            "rinnovabili", "idrico", "alluvioni", "ambientale", "ambiente",
            "territorio", "agronomo",
        ],
    ),
    (
        "Sanità e Assistenza",
        [
            "medico", "medici", "infermiere", "infermieri", "oss", "aso", "sanitario", "sanitarie", "psicologo", "psicologi",
            "veterinario", "biologo", "biologi", "fisioterapista", "fisioterapisti", "farmacista", "farmacisti", "clinica",
            "logopedista", "logopedisti", "ortottista", "ostetrica", "ostetriche", "terapista", "terapisti",
        ],
    ),
    (
        "Istruzione e Ricerca",
        [
            "docente", "docenti", "insegnante", "insegnanti", "ricercatore", "ricercatori", "ricerca", "borsista", "borsisti", "borsa di studio", "scuola", "scolastico", "scolastica",
            "università", "educatore", "educatori", "nido", "pedagogico", "pedagogista", "pedagogisti", "accademico",
            "professore", "professori",
        ],
    ),
    (
        "Polizia e Vigilanza",
        [
            "polizia", "locale", "municipale", "vigilanza", "agente", "agenti",
            "comandante", "maresciallo", "sicurezza", "vigile", "guardia",
        ],
    ),
    (
        "Sociale",
        [
            "assistente sociale", "assistenti sociali", "mediatore", "animatore", "sociologo", "sociologi",
            "welfare",
        ],
    ),
    (
        "IT e Comunicazione",
        [
            "informatico", "informatici", "digitale", "it", "ict", "software", "web", "social media",
            "comunicazione", "informazione", "sistemi", "designer", "grafico", "dati", "data", "statistico",
        ],
    ),
    (
        "Operativo e Manutentivo",
        [
            "operaio", "operai", "autista", "autisti", "cuoco", "cuochi", "giardiniere", "giardinieri", "manutentore", "manutentori",
            "conducente", "conducenti", "ormeggiatore", "operatore", "operatori", "muratore", "cantoniere",
        ],
    ),
    (
        "Amministrativo e Contabile",
        [
            "amministrativo", "amministrativi", "amministrative", "amministrazione", "procedimenti amministrativi",
            "contabile", "contabili", "contabilità", "funzionario", "funzionari", "tributi", "tributario",
            "ragioneria", "segreteria", "gestione", "ufficio", "appalti",
            "procedimenti", "supporto", "oiv", "dirigente", "dirigenti", "direttore", "direttori",
            "istruttore", "istruttori", "collaboratore", "collaboratori", "assistente", "assistenti",
            "esperto", "esperti", "impiegato", "impiegati", "segretario", "segretari", "commissario", "commissione",
            "valutazione",
        ],
    ),
]


def _matches_keywords(text: str, keywords: list[str]) -> bool:
    """Return True if *text* contains any of the keywords (case-insensitive).
    Uses regex word boundaries for short acronyms to prevent false positives."""
    text_lower = text.lower()
    for kw in keywords:
        if kw in ("it", "ict", "oss", "aso", "oiv", "scuola", "dati", "data"):
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                return True
        elif kw in text_lower:
            return True
    return False


def classify_settore(
    figura_ricercata: str | None,
    settori: list[str] | None,
) -> str:
    """Return the category that best describes the exam.

    Priority:
    1. Match keywords against *figura_ricercata*.
    2. Fall back to *settori* joined as a single string.
    3. Return 'Altro' if no match is found.
    """
    for category, keywords in _SETTORE_KEYWORDS:
        if figura_ricercata and _matches_keywords(figura_ricercata, keywords):
            return category

    if settori:
        combined = " ".join(settori)
        for category, keywords in _SETTORE_KEYWORDS:
            if _matches_keywords(combined, keywords):
                return category

    return "Altro"
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
_PREAMBLES_RE = re.compile(
    r"^(Avviso di procedura selettiva pubblica|Avviso di selezione|Concorso pubblico|Procedura comparativa|Selezione pubblica|Bando di concorso|Bando|Avviso|Selezione|Procedura|E' indetta una procedura comparativa|E' indetto un concorso pubblico|Bando CNR N\.)[^a-zA-Z]*",
    re.IGNORECASE,
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


def build_short_description(
    descrizione: str | None,
    descrizione_breve: str | None,
) -> str:
    # 1. Clean HTML
    text = clean_html_to_text(descrizione_breve or descrizione)
    if not text:
        return ""

    # 2. De-noise: Strip legal preambles
    text = _PREAMBLES_RE.sub("", text).strip()

    # 3. Format: Capitalize and end with period
    if text:
        text = text[0].upper() + text[1:]
        if not text.endswith("."):
            text += "."

    # 4. Truncate to 160 characters
    if len(text) > 160:
        text = text[:157].strip() + "..."
        if not text.endswith("."):
            text += "."

    return text


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


def clean_figura_ricercata(text: str | None, max_length: int = 100) -> str | None:
    if not text:
        return text

    text = " ".join(text.split())

    alpha_chars = [c for c in text if c.isalpha()]
    mostly_upper = False
    if alpha_chars:
        upper_chars = [c for c in alpha_chars if c.isupper()]
        mostly_upper = (len(upper_chars) / len(alpha_chars)) > 0.7

    def capitalize_word(match):
        word = match.group(0)
        if not mostly_upper and word.isupper() and len(word) > 1:
            return word
        return word.capitalize()

    cleaned = re.sub(r"[A-Za-zÀ-ÖØ-öø-ÿ]+", capitalize_word, text)

    if len(cleaned) > max_length:
        truncated = cleaned[:max_length - 3]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        cleaned = truncated + "..."

    return cleaned


def normalize_exam(raw_exam: dict[str, Any]) -> NormalizedExam:
    enti = raw_exam.get("entiRiferimento")
    municipality = enti[0] if enti and len(enti) > 0 else None
    sedi = raw_exam.get("sedi")
    region = sedi[0] if sedi and len(sedi) > 0 else None
    province = sedi[1] if sedi and len(sedi) > 1 else None
    figura_ricercata = clean_figura_ricercata(raw_exam.get("figuraRicercata"))
    settori: list[str] | None = raw_exam.get("settori") or None
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
        settore=classify_settore(figura_ricercata, settori),
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
        short_description=build_short_description(
            raw_exam.get("descrizione"), raw_exam.get("descrizioneBreve")
        ),
    )
