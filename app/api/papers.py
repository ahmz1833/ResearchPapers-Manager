from __future__ import annotations

from flask import Blueprint

bp = Blueprint("papers", __name__, url_prefix="/papers")


@bp.post("/")
def upload_paper():  # type: ignore[return-type]
    return {"message": "Not implemented"}, 501


@bp.get("/")
def search_papers():  # type: ignore[return-type]
    return {"message": "Not implemented"}, 501


@bp.get("/<paper_id>")
def paper_detail(paper_id: str):  # type: ignore[return-type]
    return {"message": "Not implemented", "paper_id": paper_id}, 501
