"""Versioned in-memory profile ingestion with downstream hooks."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from app.services.ingestion.change_detector import ChangeDetector, change_detector

IngestionHook = Callable[[dict[str, Any]], None]


class IngestionService:
    """Ingest profile snapshots and publish meaningful updates."""

    def __init__(self, detector: ChangeDetector = change_detector) -> None:
        self.detector = detector
        self._versions: dict[str, list[dict[str, Any]]] = {}
        self._hooks: list[IngestionHook] = []
        self._lock = RLock()

    def register_hook(self, hook: IngestionHook) -> None:
        """Register a watchdog, rescoring, or persistence integration hook."""
        self._hooks.append(hook)

    def ingest(
        self,
        profile: dict[str, Any] | Any,
        source: str = "api",
        force: bool = False,
    ) -> dict[str, Any]:
        """Store a new profile version when score-relevant data changed."""
        data = profile.model_dump(mode="json") if hasattr(profile, "model_dump") else deepcopy(profile)
        profile_id = str(data.get("id") or data.get("student_id") or "").strip()
        if not profile_id:
            raise ValueError("Profile id or student_id is required for ingestion.")
        with self._lock:
            previous_record = self._versions.get(profile_id, [])
            previous = previous_record[-1]["profile"] if previous_record else None
            report = self.detector.detect(previous, data)
            accepted = bool(force or report["changed"])
            version = len(previous_record) + 1 if accepted else len(previous_record)
            event = {
                "profile_id": profile_id,
                "version": version,
                "accepted": accepted,
                "source": source,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
                "change_report": report,
                "profile": deepcopy(data),
            }
            if accepted:
                self._versions.setdefault(profile_id, []).append(event)
        if accepted:
            for hook in tuple(self._hooks):
                hook(deepcopy(event))
        return event

    def latest(self, profile_id: str) -> dict[str, Any] | None:
        """Return the latest stored profile snapshot."""
        with self._lock:
            records = self._versions.get(profile_id, [])
            return deepcopy(records[-1]) if records else None

    def history(self, profile_id: str) -> list[dict[str, Any]]:
        """Return every accepted profile version."""
        with self._lock:
            return deepcopy(self._versions.get(profile_id, []))

    def compare_versions(self, profile_id: str, older: int, newer: int) -> dict[str, Any]:
        """Compare two one-based stored profile versions."""
        history = self.history(profile_id)
        if older < 1 or newer < 1 or older > len(history) or newer > len(history):
            raise IndexError("Requested profile version does not exist.")
        return self.detector.detect(history[older - 1]["profile"], history[newer - 1]["profile"])


ingestion_service = IngestionService()
