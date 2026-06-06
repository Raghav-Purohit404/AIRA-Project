"""Periodic benchmark execution and quality monitoring."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from statistics import mean
from typing import Any

from app.services.benchmark.benchmark_runner import BenchmarkCase, BenchmarkRunner


class BenchmarkSchedulerJob:
    """Run benchmark suites and evaluate latency and quality thresholds."""

    def __init__(
        self,
        suite_provider: Callable[[], list[BenchmarkCase]],
        runner: BenchmarkRunner | None = None,
        maximum_mean_latency_ms: float = 500.0,
        minimum_pass_rate: float = 0.9,
    ) -> None:
        self.suite_provider = suite_provider
        self.runner = runner or BenchmarkRunner()
        self.maximum_mean_latency_ms = maximum_mean_latency_ms
        self.minimum_pass_rate = minimum_pass_rate
        self.history: list[dict[str, Any]] = []

    def run(self) -> dict[str, Any]:
        """Run the configured suite and append monitoring metadata."""
        report = self.runner.run_suite("scheduled", self.suite_provider())
        results = report["results"]
        pass_rate = (
            sum(1 for result in results if result["passed"]) / len(results)
            if results
            else 1.0
        )
        latencies = [float(result["latency_ms"]) for result in results]
        mean_latency = mean(latencies) if latencies else 0.0
        monitored = {
            **report,
            "monitored_at": datetime.now(timezone.utc).isoformat(),
            "quality": {
                "pass_rate": round(pass_rate, 4),
                "minimum_pass_rate": self.minimum_pass_rate,
                "quality_ok": pass_rate >= self.minimum_pass_rate,
            },
            "latency": {
                "mean_ms": round(mean_latency, 3),
                "maximum_mean_ms": self.maximum_mean_latency_ms,
                "latency_ok": mean_latency <= self.maximum_mean_latency_ms,
            },
        }
        self.history.append(monitored)
        return monitored
