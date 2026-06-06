"""Profile watch loop and ingestion trigger orchestration."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Iterable
from typing import Any

from app.services.ingestion.ingestion_service import IngestionService, ingestion_service

ProfileProvider = Callable[[], Iterable[dict[str, Any] | Any]]


class ProfileWatcher:
    """Poll profile sources and submit changed snapshots for ingestion."""

    def __init__(
        self,
        provider: ProfileProvider,
        ingestion: IngestionService = ingestion_service,
        interval_seconds: float = 10.0,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("Watch interval must be positive.")
        self.provider = provider
        self.ingestion = ingestion
        self.interval_seconds = interval_seconds
        self._filesystem_hooks: list[Callable[[str], None]] = []

    def register_filesystem_hook(self, hook: Callable[[str], None]) -> None:
        """Register a future filesystem-monitoring integration hook."""
        self._filesystem_hooks.append(hook)

    def scan_once(self) -> list[dict[str, Any]]:
        """Ingest one snapshot from every provided profile."""
        return [self.ingestion.ingest(profile, source="watcher") for profile in self.provider()]

    async def run(self, stop_event: asyncio.Event | None = None) -> None:
        """Watch profiles until the optional stop event is set."""
        event = stop_event or asyncio.Event()
        while not event.is_set():
            self.scan_once()
            try:
                await asyncio.wait_for(event.wait(), timeout=self.interval_seconds)
            except TimeoutError:
                continue
