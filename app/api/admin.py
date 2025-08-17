from __future__ import annotations

from flask import Blueprint, jsonify

from ..services.view_sync import ViewSyncService

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/sync-status")
def view_sync_status():
    """
    GET /admin/sync-status
    Get current status of view synchronization for monitoring.

    Returns:
        200: {
            "pending_papers": int,
            "pending_views": int,
            "redis_keys": [string] (sample of keys)
        }
    """
    try:
        status = ViewSyncService.get_view_sync_status()
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": "Failed to get sync status"}), 500


@bp.post("/sync-now")
def manual_sync():
    """
    POST /admin/sync-now
    Manually trigger view synchronization (for testing/admin purposes).

    Returns:
        200: {
            "status": string,
            "synced_papers": int,
            "total_views_synced": int,
            "message": string
        }
    """
    try:
        result = ViewSyncService.sync_paper_views()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "message": "Manual sync failed"}), 500
