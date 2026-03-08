import hashlib
import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from app.schemas.exam import NormalizedExam


def _to_serializable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def hash_exam(exam: NormalizedExam) -> str:
    canonical = {
        "id": exam.id,
        "codice": exam.codice,
        "titolo": exam.titolo,
        "descrizione": exam.descrizione,
        "figura_ricercata": exam.figura_ricercata,
        "municipality": exam.municipality,
        "region": exam.region,
        "province": exam.province,
        "selection_criteria": exam.selection_criteria,
        "salary_range": exam.salary_range,
        "url": exam.url,
        "data_pubblicazione": _to_serializable(exam.data_pubblicazione),
        "data_scadenza": _to_serializable(exam.data_scadenza),
        "tipo_procedura": exam.tipo_procedura,
        "num_posti": exam.num_posti,
        "salary_min": _to_serializable(exam.salary_min),
        "salary_max": _to_serializable(exam.salary_max),
    }
    payload = json.dumps(canonical, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
