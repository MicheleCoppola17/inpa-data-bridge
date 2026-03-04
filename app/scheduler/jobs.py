import logging

from app.services.sync_runtime import sync_runtime

logger = logging.getLogger(__name__)


async def run_sync_job() -> None:
    result = await sync_runtime.run_once()
    logger.info(
        "sync finished fetched=%s inserted=%s updated=%s unchanged=%s failed=%s",
        result.fetched,
        result.inserted,
        result.updated,
        result.unchanged,
        result.failed,
    )
