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
    regions: list[str] = Field(default_factory=list)
    provinces: list[str] = Field(default_factory=list)
    url: str
    short_title: str
    short_description: str


class ExamPublicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    regions: list[str] = Field(default_factory=list)
    provinces: list[str] = Field(default_factory=list)
    organization: str | None = Field(None, validation_alias="municipality")
    sector: str = Field(validation_alias="settore")
    short_title: str
    short_description: str
    description: str = Field(validation_alias="descrizione")
    position: str | None = Field(None, validation_alias="figura_ricercata")
    vacancies: int | None = Field(None, validation_alias="num_posti")
    selection_criteria: list[str] = Field(default_factory=list)
    is_expired: bool
    published_at: datetime = Field(validation_alias="data_pubblicazione")
    expires_at: datetime | None = Field(None, validation_alias="data_scadenza")
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    salary_range: str | None = None
    url: str
    updated_at: datetime


class ExamPublicListResponse(BaseModel):
    items: list[ExamPublicRead]
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
