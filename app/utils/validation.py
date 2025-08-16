from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


def validate_username(username: str) -> Optional[str]:
    """Validate username: 3-20 chars, alphanumeric + underscore only."""
    if not username:
        return "Username is required"
    if not 3 <= len(username) <= 20:
        return "Username must be between 3 and 20 characters"
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, and underscores"
    return None


def validate_password(password: str) -> Optional[str]:
    """Validate password: minimum 8 characters."""
    if not password:
        return "Password is required"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    return None


def validate_email(email: str) -> Optional[str]:
    """Validate email format."""
    if not email:
        return "Email is required"
    if len(email) > 100:
        return "Email must be at most 100 characters"
    # Basic email regex
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return "Invalid email format"
    return None


def validate_name(name: str) -> Optional[str]:
    """Validate name: non-empty, max 100 chars."""
    if not name or not name.strip():
        return "Name is required"
    if len(name) > 100:
        return "Name must be at most 100 characters"
    return None


def validate_department(department: str) -> Optional[str]:
    """Validate department: non-empty, max 100 chars."""
    if not department or not department.strip():
        return "Department is required"
    if len(department) > 100:
        return "Department must be at most 100 characters"
    return None


def validate_signup_data(data: Dict[str, Any]) -> List[str]:
    """Validate all signup fields and return list of errors."""
    errors = []

    username_err = validate_username(data.get("username", ""))
    if username_err:
        errors.append(username_err)

    name_err = validate_name(data.get("name", ""))
    if name_err:
        errors.append(name_err)

    email_err = validate_email(data.get("email", ""))
    if email_err:
        errors.append(email_err)

    password_err = validate_password(data.get("password", ""))
    if password_err:
        errors.append(password_err)

    department_err = validate_department(data.get("department", ""))
    if department_err:
        errors.append(department_err)

    return errors


def validate_login_data(data: Dict[str, Any]) -> List[str]:
    """Validate login fields and return list of errors."""
    errors = []

    if not data.get("username"):
        errors.append("Username is required")

    if not data.get("password"):
        errors.append("Password is required")

    return errors
