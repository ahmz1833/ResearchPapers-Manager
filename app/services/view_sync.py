from __future__ import annotations

from typing import Any, Dict, List

import redis
from bson import ObjectId
from flask import current_app
from pymongo.database import Database


class ViewSyncService:
    """Service to sync paper view counts from Redis to MongoDB."""

    @staticmethod
    def sync_paper_views() -> Dict[str, Any]:
        """
        Sync paper view counts from Redis to MongoDB.

        Process:
        1. Get all paper_views:* keys from Redis
        2. For each key, get the view count
        3. Update MongoDB papers collection with $inc
        4. Reset Redis key to 0

        Returns dict with sync statistics.
        """
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]

        try:
            # Get all paper_views:* keys
            view_keys = redis_client.keys("paper_views:*")

            if not view_keys:
                return {
                    "status": "success",
                    "synced_papers": 0,
                    "total_views_synced": 0,
                    "message": "No paper views to sync",
                }

            synced_count = 0
            total_views = 0
            errors = []

            for key in view_keys: # type: ignore
                try:
                    # Extract paper_id from key (paper_views:paper_id)
                    paper_id = key.replace("paper_views:", "")
                    view_count = redis_client.get(key)
                    if not view_count:
                        continue

                    view_count = int(view_count) # type: ignore
                    if view_count <= 0:
                        continue

                    # Update MongoDB with $inc operation
                    result = db.papers.update_one(
                        {"_id": ObjectId(paper_id)}, {"$inc": {"views": view_count}}
                    )

                    if result.matched_count > 0:
                        redis_client.set(key, 0)
                        synced_count += 1
                        total_views += view_count
                    else:
                        errors.append(f"Paper not found: {paper_id}")

                except Exception as e:
                    errors.append(f"Error syncing {key}: {str(e)}")
                    continue

            return {
                "status": "success" if not errors else "partial_success",
                "synced_papers": synced_count,
                "total_views_synced": total_views,
                "errors": errors,
                "message": f"Synced {synced_count} papers with {total_views} total views",
            }

        except Exception as e:
            return {
                "status": "error",
                "synced_papers": 0,
                "total_views_synced": 0,
                "error": str(e),
                "message": "Failed to sync paper views",
            }

    @staticmethod
    def get_all_paper_views_keys() -> List[str]:
        """Get all paper_views:* keys from Redis for monitoring."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]
        try:
            return [
                key.decode() if isinstance(key, bytes) else key
                for key in redis_client.keys("paper_views:*") # type: ignore
            ]
        except Exception:
            return []

    @staticmethod
    def get_view_sync_status() -> Dict[str, Any]:
        """Get current status of view sync (for monitoring/debugging)."""
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        try:
            view_keys = ViewSyncService.get_all_paper_views_keys()
            total_pending_views = 0

            for key in view_keys:
                try:
                    count = redis_client.get(key)
                    if count:
                        total_pending_views += int(count) # type: ignore
                except Exception:
                    continue

            return {
                "pending_papers": len(view_keys),
                "pending_views": total_pending_views,
                "redis_keys": view_keys[:10] if len(view_keys) > 10 else view_keys,  # Show first 10
            }

        except Exception as e:
            return {"error": str(e), "pending_papers": 0, "pending_views": 0}
