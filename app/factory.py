from __future__ import annotations

from flask import Flask

from .config import Config
from .extensions import mongo_client, redis_client
from .scheduler import scheduler


def create_app() -> Flask:
    app = Flask(__name__)

    # Load configuration object
    app.config.from_object(Config())

    register_extensions(app)
    create_indexes(app)
    register_blueprints(app)
    register_healthcheck(app)
    register_scheduler(app)

    return app


def register_extensions(app: Flask) -> None:
    mongo_client.init_app(app)
    redis_client.init_app(app)


def create_indexes(app: Flask) -> None:
    """Create MongoDB indexes if not present (idempotent)."""
    from .db.indexes import ensure_indexes

    ensure_indexes(app.mongo_db)  # type: ignore[attr-defined]


def register_blueprints(app: Flask) -> None:
    from .api.auth import bp as auth_bp
    from .api.health import bp as health_bp
    from .api.papers import bp as papers_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(papers_bp)


def register_healthcheck(app: Flask) -> None:
    @app.get("/")
    def root():
        return {"app": app.config["APP_NAME"], "status": "ok"}


def register_scheduler(app: Flask) -> None:
    # Lazy start (avoid starting in interactive shell / tests inadvertently)
    if app.config.get("ENABLE_SCHEDULER", True):
        scheduler.init_app(app)
        scheduler.start()
