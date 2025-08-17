from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from flask import current_app
from pymongo.database import Database


class Paper:
    """Paper model for MongoDB operations."""

    @staticmethod
    def create(data: Dict[str, Any], user_id: str) -> str:
        """
        Create a new paper in MongoDB.
        Returns the paper_id (string) of created paper.
        """
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]

        pub_date = datetime.fromisoformat(data["publication_date"])

        paper_doc = {
            "title": data["title"],
            "authors": data["authors"],
            "abstract": data["abstract"],
            "publication_date": pub_date,
            "journal_conference": data.get("journal_conference", ""),
            "keywords": data["keywords"],
            "uploaded_by": ObjectId(user_id),
            "views": 0,
        }

        result = db.papers.insert_one(paper_doc)
        paper_id = str(result.inserted_id)

        # Insert citations if any
        citations = data.get("citations", [])
        if citations:
            Paper._create_citations(paper_id, citations)

        return paper_id

    @staticmethod
    def _create_citations(paper_id: str, cited_paper_ids: List[str]) -> None:
        """Create citation relationships in Citations collection."""
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]

        citation_docs = []
        for cited_id in cited_paper_ids:
            citation_docs.append(
                {"paper_id": ObjectId(paper_id), "cited_paper_id": ObjectId(cited_id)}
            )

        if citation_docs:
            db.citations.insert_many(citation_docs)

    @staticmethod
    def find_by_id(paper_id: str) -> Optional[Dict[str, Any]]:
        """Find paper by ObjectId. Returns paper document or None."""
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]
        try:
            return db.papers.find_one({"_id": ObjectId(paper_id)})
        except Exception:
            return None

    @staticmethod
    def search(
        search_term: str, sort_by: str = "relevance", order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Search papers using MongoDB text search.
        Returns list of paper documents formatted for API response.
        """
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]

        # Build query
        if search_term.strip():
            query = {"$text": {"$search": search_term}}
        else:
            query = {}

        # Build sort criteria
        if sort_by == "relevance" and search_term.strip():
            sort_criteria = [("score", {"$meta": "textScore"})]
            if order == "asc":
                sort_criteria = [("score", {"$meta": "textScore"})]  # text score is always desc
        else:
            # Sort by publication_date
            sort_direction = 1 if order == "asc" else -1
            sort_criteria = [("publication_date", sort_direction)]

        # Execute query
        if search_term.strip():
            cursor = db.papers.find(query, {"score": {"$meta": "textScore"}}).sort(sort_criteria)
        else:
            cursor = db.papers.find(query).sort(sort_criteria)

        # Format results for API response
        results = []
        for doc in cursor:
            results.append(
                {
                    "id": str(doc["_id"]),
                    "title": doc["title"],
                    "authors": doc["authors"],
                    "publication_date": doc["publication_date"].isoformat(),
                    "journal_conference": doc.get("journal_conference", ""),
                    "keywords": doc["keywords"],
                }
            )

        return results

    @staticmethod
    def get_citation_count(paper_id: str) -> int:
        """Get count of papers that cite this paper."""
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]
        try:
            return db.citations.count_documents({"cited_paper_id": ObjectId(paper_id)})
        except Exception:
            return 0

    @staticmethod
    def validate_citations_exist(citation_ids: List[str]) -> List[str]:
        """
        Validate that all citation IDs exist in Papers collection.
        Returns list of invalid IDs.
        """
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]
        invalid_ids = []

        for citation_id in citation_ids:
            try:
                if not db.papers.find_one({"_id": ObjectId(citation_id)}):
                    invalid_ids.append(citation_id)
            except Exception:
                invalid_ids.append(citation_id)

        return invalid_ids
