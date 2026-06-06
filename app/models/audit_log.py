"""Persistent audit trail for API actions and rescoring events."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AuditLog(Base):
    """Record who performed an action, where, and with what context."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    actor_email: Mapped[str | None] = mapped_column(String(254), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    route: Mapped[str | None] = mapped_column(String(255), nullable=True)
    entity_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, object]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False
    )

    @classmethod
    def rescoring(
        cls,
        actor_id: str | None,
        student_id: str,
        details: dict[str, object],
    ) -> "AuditLog":
        """Build a standardized rescoring audit entry."""
        return cls(
            actor_id=actor_id,
            action="student.rescored",
            route="internal://rescoring",
            entity_type="student_profile",
            entity_id=student_id,
            details=details,
        )
