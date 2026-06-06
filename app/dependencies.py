"""Shared FastAPI dependency aliases and authorization hooks."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.permissions import Role, normalize_role
from app.core.security import get_current_user
from app.db.session import get_db_session

DBSession = Annotated[Session, Depends(get_db_session)]
CurrentUser = Annotated[dict[str, object], Depends(get_current_user)]


def require_roles(*allowed_roles: Role):
    """Create a dependency that restricts an endpoint to selected roles."""
    allowed = set(allowed_roles)

    def dependency(current_user: CurrentUser) -> dict[str, object]:
        role_value = current_user.get("role")
        if not isinstance(role_value, str) or normalize_role(role_value) not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Role is not authorized.")
        return current_user

    return dependency


FacultyUser = Annotated[
    dict[str, object],
    Depends(require_roles(Role.FACULTY, Role.ADMIN)),
]
AdminUser = Annotated[dict[str, object], Depends(require_roles(Role.ADMIN))]
