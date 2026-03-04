from datetime import UTC, datetime

from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import Exam
from app.db.session import session_scope
from app.schemas.exam import SyncResult
from app.services.hasher import hash_exam
from app.services.inpa_client import InpaClient
from app.services.normalizer import normalize_exam


class SyncService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = InpaClient()

    async def sync_once(self) -> SyncResult:
        result = SyncResult()
        now = datetime.now(UTC)

        for page in range(self._settings.sync_max_pages_per_run):
            payload = await self._client.fetch_page(
                page=page,
                size=self._settings.inpa_page_size,
                payload={},
            )
            items = payload.get("content", [])
            if not items:
                break

            for raw_exam in items:
                result.fetched += 1
                try:
                    normalized = normalize_exam(raw_exam)
                    content_hash = hash_exam(normalized)
                    is_expired = (
                        normalized.data_scadenza is not None and normalized.data_scadenza < now
                    )

                    async with session_scope() as session:
                        existing = await session.scalar(select(Exam).where(Exam.id == normalized.id))

                        if existing is None:
                            session.add(
                                Exam(
                                    id=normalized.id,
                                    codice=normalized.codice,
                                    titolo=normalized.titolo,
                                    descrizione=normalized.descrizione,
                                    figura_ricercata=normalized.figura_ricercata,
                                    data_pubblicazione=normalized.data_pubblicazione,
                                    data_scadenza=normalized.data_scadenza,
                                    tipo_procedura=normalized.tipo_procedura,
                                    num_posti=normalized.num_posti,
                                    salary_min=normalized.salary_min,
                                    salary_max=normalized.salary_max,
                                    content_hash=content_hash,
                                    first_seen_at=now,
                                    last_seen_at=now,
                                    updated_at=now,
                                    is_expired=is_expired,
                                )
                            )
                            result.inserted += 1
                        elif existing.content_hash != content_hash:
                            existing.codice = normalized.codice
                            existing.titolo = normalized.titolo
                            existing.descrizione = normalized.descrizione
                            existing.figura_ricercata = normalized.figura_ricercata
                            existing.data_pubblicazione = normalized.data_pubblicazione
                            existing.data_scadenza = normalized.data_scadenza
                            existing.tipo_procedura = normalized.tipo_procedura
                            existing.num_posti = normalized.num_posti
                            existing.salary_min = normalized.salary_min
                            existing.salary_max = normalized.salary_max
                            existing.content_hash = content_hash
                            existing.last_seen_at = now
                            existing.updated_at = now
                            existing.is_expired = is_expired
                            result.updated += 1
                        else:
                            existing.last_seen_at = now
                            existing.is_expired = is_expired
                            result.unchanged += 1
                except Exception:
                    result.failed += 1

            if payload.get("last", False):
                break

        return result
