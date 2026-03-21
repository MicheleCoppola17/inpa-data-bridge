from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class NormalizedExam(BaseModel):
    id: str
    codice: str
    titolo: str
    descrizione: str
    figura_ricercata: str | None = None
    settore: str
    data_pubblicazione: datetime
    data_scadenza: datetime | None = None
    tipo_procedura: str | None = None
    selection_criteria: list[str] = Field(default_factory=list)
    num_posti: int | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    salary_range: str | None = None
    municipality: str | None = None
    region: str | None = None
    province: str | None = None
    url: str
    short_title: str
    short_description: str


class ExamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    codice: str
    titolo: str
    descrizione: str
    figura_ricercata: str | None = None
    settore: str
    data_pubblicazione: datetime
    data_scadenza: datetime | None = None
    tipo_procedura: str | None = None
    selection_criteria: list[str] = Field(default_factory=list)
    num_posti: int | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    salary_range: str | None = None
    municipality: str | None = None
    region: str | None = None
    province: str | None = None
    url: str
    short_title: str
    short_description: str
    content_hash: str
    first_seen_at: datetime
    last_seen_at: datetime
    updated_at: datetime
    is_expired: bool


class ExamListResponse(BaseModel):
    items: list[ExamRead]
    page: int
    size: int
    total: int


class SyncResult(BaseModel):
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    failed: int = 0


class SyncStatusResponse(BaseModel):
    running: bool
    scheduler_started: bool
    last_run_started_at: datetime | None = None
    last_run_finished_at: datetime | None = None
    last_success_at: datetime | None = None
    last_result: SyncResult | None = None
