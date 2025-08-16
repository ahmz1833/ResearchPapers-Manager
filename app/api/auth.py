from __future__ import annotations

import redis
from flask import Blueprint, current_app, jsonify, request

from ..models.user import User
from ..utils.validation import validate_login_data, validate_signup_data

bp = Blueprint("auth", __name__)


@bp.post("/signup")
def signup():
    """
    POST /signup
    Register a new user with unique username check via Redis.

    Body: {
        "username": string (3-20 chars, alphanumeric + underscore),
        "name": string (max 100 chars),
        "email": string (max 100 chars, valid format),
        "password": string (min 8 chars),
        "department": string (max 100 chars)
    }

    Returns:
        201: {"message": "User registered", "user_id": string}
        400: {"error": "Validation failed", "details": [errors]}
        409: {"error": "Username is already taken"}
        500: {"error": "Failed to create user"}
    """
    try:
        try:
            data = request.get_json()
        finally:
            if "data" not in locals() or not data:
                return jsonify({"error": "Invalid JSON"}), 400

        # Validate input
        errors = validate_signup_data(data)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 400

        username = data["username"]
        redis_client: redis.Redis = current_app.redis  # type: ignore[attr-defined]

        # Check Redis for username availability (HEXISTS usernames <username>)
        if redis_client.hexists("usernames", username):
            return jsonify({"error": "Username is already taken"}), 409

        try:
            user_id = User.create(data)

            # Mark username as taken in Redis (HSET usernames <username> 1)
            redis_client.hset("usernames", username, 1)

            return jsonify({"message": "User registered", "user_id": user_id}), 201

        except Exception as e:
            return jsonify({"error": "Failed to create user"}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@bp.post("/login")
def login():
    """
    POST /login
    Authenticate user and return user_id.

    Body: {
        "username": string,
        "password": string
    }

    Returns:
        200: {"message": "Login successful", "user_id": string}
        400: {"error": "Validation failed", "details": [errors]}
        401: {"error": "Invalid credentials"}
        500: {"error": "Internal server error"}
    """
    try:
        try:
            data = request.get_json()
        finally:
            if "data" not in locals() or not data:
                return jsonify({"error": "Invalid JSN"}), 400

        # Validate input
        errors = validate_login_data(data)
        if errors:
            return jsonify({"error": "Validation failed", "details": errors}), 400

        username = data["username"]
        password = data["password"]

        # Verify credentials
        user_id = User.verify_credentials(username, password)
        if not user_id:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({"message": "Login successful", "user_id": user_id}), 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
