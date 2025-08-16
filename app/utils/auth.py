from __future__ import annotations

from functools import wraps
from typing import Optional

from flask import current_app, jsonify, request

from ..models.user import User


def get_user_id_from_header() -> Optional[str]:
    """Extract user_id from X-User-ID header."""
    return request.headers.get("X-User-ID")


def require_auth(f):
    """Decorator to require valid X-User-ID header."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_user_id_from_header()
        if not user_id:
            return jsonify({"error": "X-User-ID header is required"}), 401

        # Verify user exists
        user = User.find_by_id(user_id)
        if not user:
            return jsonify({"error": "Invalid user ID"}), 401

        # Add user to kwargs for use in endpoint
        kwargs["current_user_id"] = user_id
        kwargs["current_user"] = user
        return f(*args, **kwargs)

    return decorated_function
