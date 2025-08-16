from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Config:
    APP_NAME: str = os.getenv("APP_NAME", "research-papers-manager")

    ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"

    # Scheduler interval minutes for redis->mongo sync
    VIEWS_SYNC_INTERVAL_MIN: int = int(os.getenv("VIEWS_SYNC_INTERVAL_MIN", "10"))
