import logging
from typing import Callable, Coroutine, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import Config

logger = logging.getLogger(__name__)


class BalanceScheduler:
    def __init__(self, config: Config):
        self.config = config
        self._scheduler = AsyncIOScheduler()

    def schedule_daily(self, job: Callable[[], Coroutine[Any, Any, Any]]):
        self._scheduler.add_job(
            job,
            "cron",
            hour=self.config.notification_hour,
            minute=self.config.notification_minute,
            timezone=self.config.timezone,
        )
        logger.info(f"Scheduled daily job at {self.config.notification_time} ({self.config.timezone})")

    def start(self):
        self._scheduler.start()
        logger.info("Scheduler started")

    def stop(self):
        self._scheduler.shutdown()
        logger.info("Scheduler stopped")
