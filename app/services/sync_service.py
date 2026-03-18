import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import case, delete, select
from sqlalchemy.dialects.postgresql import insert

from app.core.config import get_settings
from app.db.models import Exam
from app.db.session import session_scope
from app.schemas.exam import SyncResult
from app.services.hasher import hash_exam
from app.services.inpa_client import InpaClient
from app.services.normalizer import normalize_exam

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = InpaClient()

    async def sync_once(self) -> SyncResult:
        result = await self._run_sync()
        # After sync, cleanup old expired exams
        try:
            deleted_count = await self.delete_old_expired_exams()
            logger.info("cleanup finished deleted=%s", deleted_count)
        except Exception:
            logger.exception("cleanup failed")
        return result

    async def delete_old_expired_exams(self) -> int:
        """Deletes exams that have been expired for more than 14 days."""
        cutoff_date = datetime.now(UTC) - timedelta(days=14)
        async with session_scope() as session:
            stmt = delete(Exam).where(
                Exam.data_scadenza.is_not(None),
                Exam.data_scadenza < cutoff_date
            )
            result = await session.execute(stmt)
            return result.rowcount

    async def _run_sync(self) -> SyncResult:
        result = SyncResult()

        for page in range(self._settings.sync_max_pages_per_run):
            try:
                payload = await self._client.fetch_page(
                    page=page,
                    size=self._settings.inpa_page_size,
                    payload={},
                )
            except Exception:
                logger.exception("sync fetch failed page=%s", page)
                result.failed += 1
                break

            items = payload.get("content", [])
            if not items:
                break

            now = datetime.now(UTC)
            prepared_rows: list[dict] = []

            for raw_exam in items:
                result.fetched += 1
                try:
                    normalized = normalize_exam(raw_exam)
                    content_hash = hash_exam(normalized)
                    is_expired = (
                        normalized.data_scadenza is not None and normalized.data_scadenza < now
                    )

                    prepared_rows.append(
                        {
                            "id": normalized.id,
                            "codice": normalized.codice,
                            "titolo": normalized.titolo,
                            "descrizione": normalized.descrizione,
                            "figura_ricercata": normalized.figura_ricercata,
                            "data_pubblicazione": normalized.data_pubblicazione,
                            "data_scadenza": normalized.data_scadenza,
                            "tipo_procedura": normalized.tipo_procedura,
                            "num_posti": normalized.num_posti,
                            "salary_min": normalized.salary_min,
                            "salary_max": normalized.salary_max,
                            "municipality": normalized.municipality,
                            "region": normalized.region,
                            "province": normalized.province,
                            "salary_range": normalized.salary_range,
                            "selection_criteria": normalized.selection_criteria,
                            "url": normalized.url,
                            "short_title": normalized.short_title,
                            "content_hash": content_hash,
                            "first_seen_at": now,
                            "last_seen_at": now,
                            "updated_at": now,
                            "is_expired": is_expired,
                        }
                    )
                except Exception:
                    logger.exception("sync normalize failed")
                    result.failed += 1

            if prepared_rows:
                page_result = await self._upsert_page(prepared_rows)
                result.inserted += page_result.inserted
                result.updated += page_result.updated
                result.unchanged += page_result.unchanged

            if payload.get("last", False):
                break

        return result

    async def _upsert_page(self, rows: list[dict]) -> SyncResult:
        result = SyncResult()
        id_list = [row["id"] for row in rows]

        async with session_scope() as session:
            existing_rows = await session.execute(
                select(Exam.id, Exam.content_hash).where(Exam.id.in_(id_list))
            )
            existing_hashes = {row[0]: row[1] for row in existing_rows.all()}

            for row in rows:
                existing_hash = existing_hashes.get(row["id"])
                if existing_hash is None:
                    result.inserted += 1
                elif existing_hash != row["content_hash"]:
                    result.updated += 1
                else:
                    result.unchanged += 1

            stmt = insert(Exam).values(rows)
            excluded = stmt.excluded

            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=[Exam.id],
                set_={
                    "codice": excluded.codice,
                    "titolo": excluded.titolo,
                    "descrizione": excluded.descrizione,
                    "figura_ricercata": excluded.figura_ricercata,
                    "data_pubblicazione": excluded.data_pubblicazione,
                    "data_scadenza": excluded.data_scadenza,
                    "tipo_procedura": excluded.tipo_procedura,
                    "num_posti": excluded.num_posti,
                    "salary_min": excluded.salary_min,
                    "salary_max": excluded.salary_max,
                    "municipality": excluded.municipality,
                    "region": excluded.region,
                    "province": excluded.province,
                    "salary_range": excluded.salary_range,
                    "selection_criteria": excluded.selection_criteria,
                    "url": excluded.url,
                    "short_title": excluded.short_title,
                    "content_hash": excluded.content_hash,
                    "last_seen_at": excluded.last_seen_at,
                    "is_expired": excluded.is_expired,
                    "updated_at": case(
                        (Exam.content_hash != excluded.content_hash, excluded.updated_at),
                        else_=Exam.updated_at,
                    ),
                },
            )
            await session.execute(upsert_stmt)

        return result
