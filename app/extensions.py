from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import redis
from flask import Flask
from pymongo import MongoClient


@dataclass
class MongoExtension:
    client: Optional[MongoClient] = None

    def init_app(self, app: Flask) -> None:
        uri = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
        self.client = MongoClient(uri)
        app.mongo_client = self.client  # type: ignore[attr-defined]
        app.mongo_db = self.client[os.getenv("MONGODB_DB", "research_db")]  # type: ignore[attr-defined]


@dataclass
class RedisExtension:
    client: Optional[redis.Redis] = None

    def init_app(self, app: Flask) -> None:
        url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.client = redis.Redis.from_url(url, decode_responses=True)
        app.redis = self.client  # type: ignore[attr-defined]


mongo_client = MongoExtension()
redis_client = RedisExtension()
