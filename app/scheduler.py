from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask


class SchedulerWrapper:
    def __init__(self) -> None:
        self._scheduler: BackgroundScheduler | None = None

    def init_app(self, app: Flask) -> None:
        self._scheduler = BackgroundScheduler(timezone="UTC")
        interval = app.config.get("VIEWS_SYNC_INTERVAL_MIN", 10)
        # Placeholder job (to implement sync logic later)
        self._scheduler.add_job(
            func=self._placeholder_job,
            trigger="interval",
            minutes=interval,
            id="views_sync",
            replace_existing=True,
            max_instances=1,
        )

    def start(self) -> None:
        if self._scheduler and not self._scheduler.running:
            self._scheduler.start()

    def _placeholder_job(self) -> None:  # pragma: no cover - will be replaced
        pass


scheduler = SchedulerWrapper()
