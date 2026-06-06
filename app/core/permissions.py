"""Role and permission helpers for FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Iterable
from enum import StrEnum

from fastapi import HTTPException, status


class Role(StrEnum):
    """Supported AIRA user roles."""

    ADMIN = "admin"
    FACULTY = "faculty"
    STUDENT = "student"
    RECRUITER = "recruiter"


ROLE_PERMISSIONS: dict[Role, set[str]] = {
    Role.ADMIN: {"*"},
    Role.FACULTY: {"students:read", "jd:read", "analytics:read", "feedback:read"},
    Role.STUDENT: {"profile:read", "profile:update", "feedback:read"},
    Role.RECRUITER: {"jd:read", "analytics:read"},
}


def normalize_role(role: str | Role) -> Role:
    """Convert arbitrary role text to a supported Role enum."""
    try:
        return role if isinstance(role, Role) else Role(role.lower())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unsupported role.",
        ) from exc


def has_permission(role: str | Role, permission: str) -> bool:
    """Return whether a role grants a permission."""
    normalized_role = normalize_role(role)
    permissions = ROLE_PERMISSIONS[normalized_role]
    return "*" in permissions or permission in permissions


def require_permissions(role: str | Role, required_permissions: Iterable[str]) -> None:
    """Raise a 403 error unless a role includes all required permissions."""
    missing = [permission for permission in required_permissions if not has_permission(role, permission)]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"message": "Insufficient permissions.", "missing": missing},
        )
