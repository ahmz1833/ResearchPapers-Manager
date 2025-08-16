from __future__ import annotations

from flask import Blueprint

bp = Blueprint("auth", __name__, url_prefix="/")

# Placeholder routes (implement later)
@bp.post("/signup")
def signup():  # type: ignore[return-type]
    return {"message": "Not implemented"}, 501


@bp.post("/login")
def login():  # type: ignore[return-type]
    return {"message": "Not implemented"}, 501
