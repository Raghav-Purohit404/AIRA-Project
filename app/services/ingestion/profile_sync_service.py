"""Profile synchronization event preparation."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.services.ingestion.change_detector import ChangeDetector

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProfileSyncEvent:
    """A profile update event prepared for downstream pipelines."""

    profile_id: str
    changed_fields: list[str]
    changes: list[dict[str, Any]]
    requires_rescoring: bool
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable event."""
        return {
            "profile_id": self.profile_id,
            "changed_fields": self.changed_fields,
            "changes": self.changes,
            "requires_rescoring": self.requires_rescoring,
            "generated_at": self.generated_at,
        }


class ProfileSyncService:
    """Detect profile updates and generate synchronization events."""

    RESCORING_FIELDS = {"academic", "skills", "projects", "internships", "hackathons", "achievements"}

    def __init__(self, change_detector: ChangeDetector | None = None) -> None:
        self.change_detector = change_detector or ChangeDetector()

    def prepare_sync_event(
        self,
        profile_id: str,
        previous: dict[str, Any] | None,
        current: dict[str, Any],
    ) -> ProfileSyncEvent:
        """Prepare a sync event without triggering downstream rescoring."""
        report = self.change_detector.detect(previous or {}, current)
        changed_fields = [str(field_name) for field_name in report.get("changed_fields", [])]
        requires_rescoring = bool(self.RESCORING_FIELDS.intersection(changed_fields))
        event = ProfileSyncEvent(
            profile_id=profile_id,
            changed_fields=changed_fields,
            changes=list(report.get("changes", [])),
            requires_rescoring=requires_rescoring,
        )
        logger.info("Prepared profile sync event for %s with fields=%s", profile_id, changed_fields)
        return event


profile_sync_service = ProfileSyncService()
