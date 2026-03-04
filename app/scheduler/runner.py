from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.scheduler.jobs import run_sync_job
from app.services.sync_runtime import sync_runtime


class SchedulerRunner:
    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._started = False

    def start(self) -> None:
        if self._started:
            return

        settings = get_settings()
        self._scheduler.add_job(
            run_sync_job,
            trigger=CronTrigger.from_crontab(settings.sync_cron),
            id="inpa_sync",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        self._started = True
        sync_runtime.set_scheduler_started(True)

    def stop(self) -> None:
        if not self._started:
            return
        self._scheduler.shutdown(wait=False)
        self._started = False
        sync_runtime.set_scheduler_started(False)
