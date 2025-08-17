from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional


def validate_title(title: str) -> Optional[str]:
    """Validate paper title: required, max 200 chars."""
    if not title or not title.strip():
        return "Title is required"
    if len(title) > 200:
        return "Title must be at most 200 characters"
    return None


def validate_abstract(abstract: str) -> Optional[str]:
    """Validate paper abstract: required, max 1000 chars."""
    if not abstract or not abstract.strip():
        return "Abstract is required"
    if len(abstract) > 1000:
        return "Abstract must be at most 1000 characters"
    return None


def validate_authors(authors: List[str]) -> Optional[str]:
    """Validate authors: 1-5 items, each max 100 chars."""
    if not authors or len(authors) == 0:
        return "At least one author is required"
    if len(authors) > 5:
        return "Maximum 5 authors allowed"

    for author in authors:
        if not author or not author.strip():
            return "Author names cannot be empty"
        if len(author) > 100:
            return "Each author name must be at most 100 characters"

    return None


def validate_keywords(keywords: List[str]) -> Optional[str]:
    """Validate keywords: 1-5 items, each max 50 chars."""
    if not keywords or len(keywords) == 0:
        return "At least one keyword is required"
    if len(keywords) > 5:
        return "Maximum 5 keywords allowed"

    for keyword in keywords:
        if not keyword or not keyword.strip():
            return "Keywords cannot be empty"
        if len(keyword) > 50:
            return "Each keyword must be at most 50 characters"

    return None


def validate_publication_date(date_str: str) -> Optional[str]:
    """Validate ISO date format (YYYY-MM-DD)."""
    if not date_str:
        return "Publication date is required"

    try:
        datetime.fromisoformat(date_str)
        return None
    except ValueError:
        return "Publication date must be in ISO format (YYYY-MM-DD)"


def validate_journal_conference(journal: str) -> Optional[str]:
    """Validate journal/conference: optional, max 200 chars."""
    if journal and len(journal) > 200:
        return "Journal/conference must be at most 200 characters"
    return None


def validate_citations(citations: List[str]) -> Optional[str]:
    """Validate citations: 0-5 paper IDs."""
    if len(citations) > 5:
        return "Maximum 5 citations allowed"

    # Check ObjectId format (24 hex characters)
    for citation_id in citations:
        if not re.match(r"^[0-9a-fA-F]{24}$", citation_id):
            return f"Invalid citation ID format: {citation_id}"

    return None


def validate_paper_data(data: Dict[str, Any]) -> List[str]:
    """Validate all paper fields and return list of errors."""
    errors = []

    title_err = validate_title(data.get("title", ""))
    if title_err:
        errors.append(title_err)

    abstract_err = validate_abstract(data.get("abstract", ""))
    if abstract_err:
        errors.append(abstract_err)

    authors = data.get("authors", [])
    if not isinstance(authors, list):
        errors.append("Authors must be a list")
    else:
        authors_err = validate_authors(authors)
        if authors_err:
            errors.append(authors_err)

    keywords = data.get("keywords", [])
    if not isinstance(keywords, list):
        errors.append("Keywords must be a list")
    else:
        keywords_err = validate_keywords(keywords)
        if keywords_err:
            errors.append(keywords_err)

    date_err = validate_publication_date(data.get("publication_date", ""))
    if date_err:
        errors.append(date_err)

    journal_err = validate_journal_conference(data.get("journal_conference", ""))
    if journal_err:
        errors.append(journal_err)

    citations = data.get("citations", [])
    if not isinstance(citations, list):
        errors.append("Citations must be a list")
    else:
        citations_err = validate_citations(citations)
        if citations_err:
            errors.append(citations_err)

    return errors


def validate_search_params(search: str, sort_by: str, order: str) -> List[str]:
    """Validate search query parameters."""
    errors = []

    if sort_by not in ["publication_date", "relevance"]:
        errors.append("sort_by must be 'publication_date' or 'relevance'")

    if order not in ["asc", "desc"]:
        errors.append("order must be 'asc' or 'desc'")

    return errors
