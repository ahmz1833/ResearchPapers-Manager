from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask


class SchedulerWrapper:
    def __init__(self) -> None:
        self._scheduler: BackgroundScheduler | None = None

    def init_app(self, app: Flask) -> None:
        self._scheduler = BackgroundScheduler(timezone="UTC")
        interval = app.config.get("VIEWS_SYNC_INTERVAL_MIN", 10)

        # Background job to sync Redis paper views to MongoDB
        self._scheduler.add_job(
            func=self._sync_paper_views_job,
            trigger="interval",
            minutes=interval,
            id="views_sync",
            replace_existing=True,
            max_instances=1,
            name="Sync Paper Views from Redis to MongoDB",
        )

        # Store app context for job execution
        self._app = app

    def start(self) -> None:
        if self._scheduler and not self._scheduler.running:
            self._scheduler.start()
            logging.info("Background scheduler started")

    def _sync_paper_views_job(self) -> None:
        """
        Background job that syncs paper view counts from Redis to MongoDB.
        Runs every 10 minutes (or as configured).

        1. Retrieve all paper_views:* keys using KEYS paper_views:*
        2. For each key, GET the count
        3. Update MongoDB Papers collection with $inc: { views: count }
        4. SET Redis key to 0 to reset counter
        """
        if not hasattr(self, "_app"):
            logging.error("No app context available for sync job")
            return

        with self._app.app_context():
            try:
                from .services.view_sync import ViewSyncService

                # Perform the sync operation
                result = ViewSyncService.sync_paper_views()

                # Log the result
                if result["status"] == "success":
                    logging.info(
                        f"View sync completed: {result['synced_papers']} papers, "
                        f"{result['total_views_synced']} views synced"
                    )
                elif result["status"] == "partial_success":
                    logging.warning(
                        f"View sync partially completed: {result['synced_papers']} papers, "
                        f"{result['total_views_synced']} views synced. "
                        f"Errors: {len(result.get('errors', []))}"
                    )
                else:
                    logging.error(f"View sync failed: {result.get('error', 'Unknown error')}")

            except Exception as e:
                logging.error(f"Critical error in view sync job: {str(e)}")

    def shutdown(self) -> None:
        """Gracefully shutdown the scheduler."""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown()
            logging.info("Background scheduler stopped")


scheduler = SchedulerWrapper()
