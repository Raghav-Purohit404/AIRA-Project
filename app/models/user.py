"""Persistent user model for local and future PostgreSQL authentication."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.password_utils import hash_password, verify_password
from app.db.database import Base


class UserRole(StrEnum):
    """Persistent roles supported by the authentication pipeline."""

    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"


class User(Base):
    """Application identity compatible with password and OAuth login."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, native_enum=False), default=UserRole.STUDENT)
    password_hash: Mapped[str | None] = mapped_column(String(512), nullable=True)
    google_subject: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def set_password(self, password: str) -> None:
        """Hash and store a password using the shared auth helper."""
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """Validate a password when this account has local credentials."""
        return bool(self.password_hash and verify_password(password, self.password_hash))

    def jwt_claims(self) -> dict[str, str]:
        """Return stable claims used by the JWT handler."""
        return {"user_id": self.id, "email": self.email, "role": self.role.value, "full_name": self.full_name}
