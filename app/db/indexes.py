from __future__ import annotations

from pymongo.database import Database


def ensure_indexes(db: Database) -> None:
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
