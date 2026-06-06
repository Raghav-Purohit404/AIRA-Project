"""In-memory monitoring service for health and latency snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.utils.metrics import runtime_metrics


@dataclass
class MonitoringService:
    """Collect lightweight runtime metrics without external dependencies."""

    service_name: str = "aira-backend"
    latencies_ms: list[float] = field(default_factory=list)

    def record_latency(self, latency_ms: float) -> None:
        """Record one latency measurement in milliseconds."""
        self.latencies_ms.append(max(0.0, latency_ms))

    def snapshot(self) -> dict[str, object]:
        """Return a structured health and monitoring snapshot."""
        average_latency = (
            round(sum(self.latencies_ms) / len(self.latencies_ms), 2)
            if self.latencies_ms
            else 0.0
        )
        return {
            "success": True,
            "service": self.service_name,
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "latency_count": len(self.latencies_ms),
                "average_latency_ms": average_latency,
                "runtime": runtime_metrics.snapshot(),
            },
        }
