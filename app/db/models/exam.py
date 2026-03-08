from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    codice: Mapped[str] = mapped_column(Text, nullable=False)
    titolo: Mapped[str] = mapped_column(Text, nullable=False)
    descrizione: Mapped[str] = mapped_column(Text, nullable=False)
    figura_ricercata: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_pubblicazione: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    data_scadenza: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tipo_procedura: Mapped[str | None] = mapped_column(Text, nullable=True)
    num_posti: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    municipality: Mapped[str | None] = mapped_column(Text, nullable=True)
    region: Mapped[str | None] = mapped_column(Text, nullable=True)
    province: Mapped[str | None] = mapped_column(Text, nullable=True)
    salary_range: Mapped[str | None] = mapped_column(Text, nullable=True)
    selection_criteria: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    short_title: Mapped[str] = mapped_column(Text, nullable=False)
