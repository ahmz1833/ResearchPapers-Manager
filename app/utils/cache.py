from __future__ import annotations

import json
from typing import Any, Dict, Optional

import redis
from flask import current_app


class CacheService:
    """Redis caching service for search results and username management."""

    @staticmethod
    def _get_search_key(search_term: str, sort_by: str, order: str) -> str:
        """Generate Redis key for search cache."""
        clean_term = search_term.strip().replace(" ", "_").replace(":", "_")
        if not clean_term:
            clean_term = "all"
        return f"search:{clean_term}:{sort_by}:{order}"

    @staticmethod
    def get_cached_search(search_term: str, sort_by: str, order: str) -> Optional[Dict[str, Any]]:
        """Get cached search results from Redis."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        key = CacheService._get_search_key(search_term, sort_by, order)
        cached_data = redis_client.get(key)

        if cached_data:
            try:
                return json.loads(cached_data)  # type: ignore
            except json.JSONDecodeError:
                redis_client.delete(key)  # Invalid JSON, remove from cache

        return None

    @staticmethod
    def cache_search_results(
        search_term: str, sort_by: str, order: str, results: Dict[str, Any]
    ) -> None:
        """Cache search results in Redis with 5 minute TTL."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        key = CacheService._get_search_key(search_term, sort_by, order)

        try:
            redis_client.setex(key, 300, json.dumps(results))  # Cache for 300 seconds (5 minutes)
        except Exception:
            pass

    @staticmethod
    def increment_paper_views(paper_id: str) -> int:
        """Increment paper view count in Redis and return current count."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        key = f"paper_views:{paper_id}"
        try:
            return redis_client.incr(key)  # type: ignore
        except Exception:
            return 0

    @staticmethod
    def get_paper_views(paper_id: str) -> int:
        """Get current paper view count from Redis."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        key = f"paper_views:{paper_id}"
        try:
            views = redis_client.get(key)
            return int(views) if views else 0  # type: ignore
        except Exception:
            return 0

    @staticmethod
    def is_username_taken(username: str) -> bool:
        """Check if username exists in Redis cache."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        try:
            return bool(redis_client.hexists("usernames", username))
        except Exception:
            return False

    @staticmethod
    def add_username_to_cache(username: str) -> None:
        """Add username to Redis cache"""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        try:
            redis_client.hset("usernames", username, 1)  # type: ignore
        except Exception:
            pass

    @staticmethod
    def invalidate_search_cache() -> None:
        """Invalidate all search cache entries (called when new papers are added)."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        try:
            search_keys = redis_client.keys("search:*")
            if search_keys:
                redis_client.delete(*search_keys)  # type: ignore
        except Exception:
            pass
