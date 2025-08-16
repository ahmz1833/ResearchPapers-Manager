from __future__ import annotations

from typing import Any, Dict, Optional

from bson import ObjectId
from flask import current_app
from pymongo.database import Database

from ..utils.password import hash_password, verify_password


class User:
    """User model for MongoDB operations."""

    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        """
        Create a new user in MongoDB.
        Returns the user_id (string) of created user.
        """
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]

        # Hash the password
        hashed_password = hash_password(data["password"])

        # Prepare user document
        user_doc = {
            "username": data["username"],
            "name": data["name"],
            "email": data["email"],
            "password": hashed_password,
            "department": data["department"],
        }

        # Insert to MongoDB
        result = db.users.insert_one(user_doc)
        return str(result.inserted_id)

    @staticmethod
    def find_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Find user by username. Returns user document or None."""
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]
        return db.users.find_one({"username": username})

    @staticmethod
    def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ObjectId. Returns user document or None."""
        db: Database = current_app.mongo_db  # type: ignore[attr-defined]
        try:
            return db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    @staticmethod
    def verify_credentials(username: str, password: str) -> Optional[str]:
        """
        Verify username/password credentials.
        Returns user_id (string) if valid, None if invalid.
        """
        user = User.find_by_username(username)
        if not user:
            return None

        if verify_password(password, user["password"]):
            return str(user["_id"])

        return None
