from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class NormalizedExam(BaseModel):
    id: str
    codice: str
    titolo: str
    descrizione: str
    figura_ricercata: str | None = None
    data_pubblicazione: datetime
    data_scadenza: datetime | None = None
    tipo_procedura: str | None = None
    num_posti: int | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None


class SyncResult(BaseModel):
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0
