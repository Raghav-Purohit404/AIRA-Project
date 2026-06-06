"""Runtime metrics helpers for requests, APIs, and service uptime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def safe_divide(numerator: float, denominator: float) -> float:
    """Divide two numbers and return 0 when the denominator is zero."""
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def percentage(numerator: float, denominator: float) -> float:
    """Return a percentage with two decimal places."""
    return round(safe_divide(numerator, denominator) * 100.0, 2)


@dataclass
class RuntimeMetrics:
    """In-memory runtime metrics registry."""

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    request_count: int = 0
    api_counts: dict[str, int] = field(default_factory=dict)
    error_count: int = 0
    service_counts: dict[str, int] = field(default_factory=dict)

    def increment_request(self, path: str | None = None) -> None:
        """Increment total request count and optional path counter."""
        self.request_count += 1
        if path:
            self.increment_api(path)

    def increment_api(self, path: str) -> None:
        """Increment a route/path counter."""
        self.api_counts[path] = self.api_counts.get(path, 0) + 1

    def increment_service(self, service_name: str) -> None:
        """Increment a service execution counter."""
        self.service_counts[service_name] = self.service_counts.get(service_name, 0) + 1

    def increment_error(self) -> None:
        """Increment the error counter."""
        self.error_count += 1

    def uptime_seconds(self) -> float:
        """Return service uptime in seconds."""
        return round((datetime.now(timezone.utc) - self.started_at).total_seconds(), 3)

    def snapshot(self) -> dict[str, object]:
        """Return a JSON-serializable runtime metrics snapshot."""
        return {
            "started_at": self.started_at.isoformat(),
            "uptime_seconds": self.uptime_seconds(),
            "request_count": self.request_count,
            "api_counts": dict(sorted(self.api_counts.items())),
            "service_counts": dict(sorted(self.service_counts.items())),
            "error_count": self.error_count,
            "error_rate_percent": percentage(self.error_count, self.request_count),
        }


runtime_metrics = RuntimeMetrics()
