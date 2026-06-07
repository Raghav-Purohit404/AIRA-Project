"""Latency measurement utilities for AIRA pipelines."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any

from app.core.constants import BENCHMARK_THRESHOLDS


class LatencyBenchmark:
    """Measure response times for named pipeline callables."""

    def run(self, pipelines: dict[str, Callable[[], Any]]) -> dict[str, Any]:
        """Execute pipeline callables and return latency statistics."""
        results: list[dict[str, Any]] = []
        for name, pipeline in pipelines.items():
            start = perf_counter()
            error: str | None = None
            try:
                pipeline()
            except Exception as exc:
                error = str(exc)
            latency_ms = round((perf_counter() - start) * 1000.0, 3)
            results.append(
                {
                    "name": name,
                    "latency_ms": latency_ms,
                    "passed": error is None and latency_ms <= BENCHMARK_THRESHOLDS["maximum_latency_ms"],
                    "error": error,
                }
            )
        return {
            "success": all(result["passed"] for result in results),
            "benchmark": "latency_benchmark",
            "summary": {"pipeline_count": len(results)},
            "results": results,
        }


latency_benchmark = LatencyBenchmark()
