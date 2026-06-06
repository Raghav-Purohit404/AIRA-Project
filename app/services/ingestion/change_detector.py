"""Structured student profile change detection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FieldChange:
    """Before-and-after values for one profile field."""

    field: str
    before: Any
    after: Any
    added: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the change for APIs and audit logs."""
        return {
            "field": self.field,
            "before": self.before,
            "after": self.after,
            "added": list(self.added),
            "removed": list(self.removed),
        }


class ChangeDetector:
    """Compare profile versions across score-relevant fields."""

    tracked_fields = ("skills", "cgpa", "projects", "internships")

    def detect(self, previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
        """Return a structured report of score-relevant changes."""
        if previous is None:
            return {
                "changed": True,
                "is_initial": True,
                "changed_fields": list(self.tracked_fields),
                "changes": [
                    FieldChange(field, None, self._value(current, field)).to_dict()
                    for field in self.tracked_fields
                ],
            }

        changes: list[FieldChange] = []
        for field in self.tracked_fields:
            before = self._value(previous, field)
            after = self._value(current, field)
            if self._canonical(before) == self._canonical(after):
                continue
            if field in {"skills", "projects", "internships"}:
                before_labels = set(self._labels(before))
                after_labels = set(self._labels(after))
                changes.append(
                    FieldChange(
                        field=field,
                        before=before,
                        after=after,
                        added=tuple(sorted(after_labels - before_labels)),
                        removed=tuple(sorted(before_labels - after_labels)),
                    )
                )
            else:
                changes.append(FieldChange(field, before, after))
        return {
            "changed": bool(changes),
            "is_initial": False,
            "changed_fields": [change.field for change in changes],
            "changes": [change.to_dict() for change in changes],
        }

    @staticmethod
    def _value(profile: dict[str, Any], field: str) -> Any:
        """Read both flattened and aggregate profile representations."""
        if field == "cgpa":
            academic = profile.get("academic", {})
            return academic.get("cgpa") if isinstance(academic, dict) else profile.get("cgpa")
        return profile.get(field, [])

    @staticmethod
    def _labels(items: Any) -> list[str]:
        """Extract stable labels from list-like profile values."""
        if not isinstance(items, list):
            return []
        labels: list[str] = []
        for item in items:
            if isinstance(item, dict):
                label = item.get("name") or item.get("title") or item.get("company") or item.get("role")
            else:
                label = item
            if label is not None:
                labels.append(str(label).strip().casefold())
        return labels

    @classmethod
    def _canonical(cls, value: Any) -> Any:
        """Normalize nested values for order-insensitive comparisons."""
        if isinstance(value, dict):
            return tuple(sorted((key, cls._canonical(item)) for key, item in value.items()))
        if isinstance(value, list):
            return tuple(sorted((repr(cls._canonical(item)) for item in value)))
        return value


change_detector = ChangeDetector()


def detect_changes(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    """Convenience wrapper for profile change detection."""
    return change_detector.detect(previous, current)
