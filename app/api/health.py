from __future__ import annotations

from flask import Blueprint, current_app

bp = Blueprint("health", __name__, url_prefix="/health")


@bp.get("/")
def health() -> dict:
    # Shallow health info (no blocking ping calls)
    return {
        "app": current_app.config.get("APP_NAME"),
        "mongo": bool(getattr(current_app, "mongo_client", None)),
        "redis": bool(getattr(current_app, "redis", None)),
        "status": "ok",
    }
