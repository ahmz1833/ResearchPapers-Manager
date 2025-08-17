from __future__ import annotations

from flask import Blueprint, jsonify, request

from ..models.paper import Paper
from ..utils.auth import require_auth
from ..utils.cache import CacheService
from ..utils.paper_validation import validate_paper_data, validate_search_params

bp = Blueprint("papers", __name__, url_prefix="/papers")


@bp.post("/")
@require_auth
def upload_paper(current_user_id: str, current_user: dict):
    """
    POST /papers
    Upload a new paper with authentication via X-User-ID header.

    Headers: X-User-ID: <user_id>
    Body: {
        "title": string (required, max 200 chars),
        "authors": [string] (1-5 items, each max 100 chars),
        "abstract": string (required, max 1000 chars),
        "publication_date": string (ISO format YYYY-MM-DD),
        "journal_conference": string (optional, max 200 chars),
        "keywords": [string] (1-5 items, each max 50 chars),
        "citations": [string] (0-5 valid paper IDs)
    }

    Returns:
        201: {"message": "Paper uploaded", "paper_id": string}
        400: {"error": "Validation failed", "details": [errors]}
        401: {"error": "X-User-ID header is required"}
        404: {"error": "Invalid citation IDs", "details": [invalid_ids]}
        500: {"error": "Failed to create paper"}
    """
    try:
        try:
            data = request.get_json()
        finally:
            if "data" not in locals() or not data:
                return jsonify({"error": "Invalid JSON"}), 400

        # Validate input
        errors = validate_paper_data(data)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 400

        # Validate citations exist in Papers collection
        citations = data.get("citations", [])
        if citations:
            invalid_citations = Paper.validate_citations_exist(citations)
            if invalid_citations:
                return jsonify({"error": "Invalid citation IDs", "details": invalid_citations}), 404

        try:
            paper_id = Paper.create(data, current_user_id)  # Create paper in MongoDB and citations
            CacheService.invalidate_search_cache()  # Invalidate search cache since we added a new paper
            return jsonify({"message": "Paper uploaded", "paper_id": paper_id}), 201

        except Exception as e:
            return jsonify({"error": "Failed to create paper"}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@bp.get("/")
def search_papers():
    """
    GET /papers
    Search papers with optional text search and sorting.

    Query params:
        ?search=string (optional, default: "")
        ?sort_by=string (optional, "publication_date" or "relevance", default: "relevance")
        ?order=string (optional, "asc" or "desc", default: "desc")

    Returns:
        200: {"papers": [{"id": string, "title": string, "authors": [string],
                         "publication_date": string, "journal_conference": string,
                         "keywords": [string]}]}
        400: {"error": "Invalid query parameters", "details": [errors]}
        500: {"error": "Internal server error"}
    """
    try:
        # Get query parameters with defaults
        search_term = request.args.get("search", "").strip()
        sort_by = request.args.get("sort_by", "relevance")
        order = request.args.get("order", "desc")

        # Validate query parameters
        errors = validate_search_params(search_term, sort_by, order)
        if errors:
            return jsonify({"error": "Invalid query parameters", "details": errors}), 400

        # Check Redis cache first
        cached_result = CacheService.get_cached_search(search_term, sort_by, order)
        if cached_result:
            return jsonify(cached_result), 200

        # Query MongoDB
        papers = Paper.search(search_term, sort_by, order)
        result = {"papers": papers}

        # Cache the results in Redis
        CacheService.cache_search_results(search_term, sort_by, order, result)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@bp.get("/<paper_id>")
def paper_detail(paper_id: str):
    """
    GET /papers/<paper_id>
    Get paper details with citation count and view tracking.

    Returns:
        200: {"id": string, "title": string, "authors": [string], "abstract": string,
              "publication_date": string, "journal_conference": string,
              "keywords": [string], "citation_count": int, "views": int}
        404: {"error": "Paper not found"}
        500: {"error": "Internal server error"}
    """
    try:
        paper = Paper.find_by_id(paper_id)
        if not paper:
            return jsonify({"error": "Paper not found"}), 404

        CacheService.increment_paper_views(paper_id)  # Increment view count in Redis
        redis_views = CacheService.get_paper_views(paper_id)  # Get current view count from Redis
        citation_count = Paper.get_citation_count(paper_id)  # Get citation count from MongoDB
        total_views = (
            paper.get("views", 0) + redis_views
        )  # Total views = MongoDB views + Redis views

        result = {
            "id": str(paper["_id"]),
            "title": paper["title"],
            "authors": paper["authors"],
            "abstract": paper["abstract"],
            "publication_date": paper["publication_date"].isoformat(),
            "journal_conference": paper.get("journal_conference", ""),
            "keywords": paper["keywords"],
            "citation_count": citation_count,
            "views": total_views,
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
