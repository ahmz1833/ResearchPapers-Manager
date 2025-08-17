from __future__ import annotations

from flask import Flask

from .config import Config
from .extensions import mongo_client, redis_client
from .scheduler import scheduler


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    register_extensions(app)
    register_indexes(app)
    register_blueprints(app)
    register_healthcheck(app)
    register_scheduler(app)
    return app


def register_extensions(app: Flask) -> None:
    mongo_client.init_app(app)
    redis_client.init_app(app)


def register_blueprints(app: Flask) -> None:
    from .api.admin import bp as admin_bp
    from .api.auth import bp as auth_bp
    from .api.health import bp as health_bp
    from .api.papers import bp as papers_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(admin_bp)


def register_scheduler(app: Flask) -> None:
    if not app.config.get("ENABLE_SCHEDULER", True):
        return
    # Use an internal flag instead of nonexistent 'running' attribute
    if not getattr(scheduler, "_started", False):
        scheduler.init_app(app)
        scheduler.start()
        setattr(scheduler, "_started", True)
        app.logger.info("Background scheduler started")


def register_indexes(app: Flask) -> None:
    """Create MongoDB indexes if not present (idempotent)."""
    db = app.mongo_db  # type: ignore
    # Users: unique username
    db.users.create_index("username", unique=True, name="ux_username")
    # Papers: text index for search
    db.papers.create_index(
        [("title", "text"), ("abstract", "text"), ("keywords", "text")],
        name="text_papers",
        default_language="english",
    )
    # Citations: index on cited_paper_id
    db.citations.create_index("cited_paper_id", name="ix_cited_paper")


def register_healthcheck(app: Flask) -> None:
    @app.get("/")
    def root():
        return {"app": app.config["APP_NAME"], "status": "ok"}
