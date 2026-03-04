import asyncio
from datetime import UTC, datetime

from app.schemas.exam import SyncResult, SyncStatusResponse
from app.services.sync_service import SyncService


class SyncRuntime:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._running = False
        self._scheduler_started = False
        self._last_run_started_at: datetime | None = None
        self._last_run_finished_at: datetime | None = None
        self._last_success_at: datetime | None = None
        self._last_result: SyncResult | None = None

    def set_scheduler_started(self, started: bool) -> None:
        self._scheduler_started = started

    async def run_once(self) -> SyncResult:
        async with self._lock:
            if self._running:
                return self._last_result or SyncResult()
            self._running = True

        self._last_run_started_at = datetime.now(UTC)
        try:
            result = await SyncService().sync_once()
            self._last_result = result
            self._last_success_at = datetime.now(UTC)
            return result
        finally:
            self._last_run_finished_at = datetime.now(UTC)
            self._running = False

    def is_running(self) -> bool:
        return self._running

    def build_status(self) -> SyncStatusResponse:
        return SyncStatusResponse(
            running=self._running,
            scheduler_started=self._scheduler_started,
            last_run_started_at=self._last_run_started_at,
            last_run_finished_at=self._last_run_finished_at,
            last_success_at=self._last_success_at,
            last_result=self._last_result,
        )


sync_runtime = SyncRuntime()
