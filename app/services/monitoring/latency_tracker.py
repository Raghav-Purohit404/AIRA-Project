"""Execution latency tracking for application pipelines."""

from __future__ import annotations

from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Iterator


@dataclass
class LatencyTracker:
    """Collect and aggregate named execution durations."""

    _samples: dict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def record(self, name: str, duration_ms: float) -> None:
        """Record a measured duration."""
        self._samples[name].append(round(max(0.0, duration_ms), 3))

    @contextmanager
    def track(self, name: str) -> Iterator[None]:
        """Context manager that records elapsed time for a block."""
        start = perf_counter()
        try:
            yield
        finally:
            self.record(name, (perf_counter() - start) * 1000.0)

    def summary(self) -> dict[str, dict[str, float]]:
        """Return count, mean, min, max, and latest latency by name."""
        result: dict[str, dict[str, float]] = {}
        for name, samples in self._samples.items():
            result[name] = {
                "count": float(len(samples)),
                "mean_ms": round(sum(samples) / len(samples), 3),
                "min_ms": min(samples),
                "max_ms": max(samples),
                "latest_ms": samples[-1],
            }
        return result

    def reset(self) -> None:
        """Clear all samples."""
        self._samples.clear()


latency_tracker = LatencyTracker()
