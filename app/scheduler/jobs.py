import logging

from app.services.sync_service import SyncService

logger = logging.getLogger(__name__)


async def run_sync_job() -> None:
    service = SyncService()
    result = await service.sync_once()
    logger.info(
        "sync finished fetched=%s inserted=%s updated=%s unchanged=%s failed=%s",
        result.fetched,
        result.inserted,
        result.updated,
        result.unchanged,
        result.failed,
    )
