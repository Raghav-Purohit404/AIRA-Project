"""Benchmark runner for local deterministic evaluations."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any

from app.services.benchmark.evaluation_metrics import accuracy_score, mean_latency


@dataclass(frozen=True)
class BenchmarkCase:
    """A single benchmark case."""

    name: str
    runner: Callable[[], Any]
    expected: Any | None = None


@dataclass
class BenchmarkReport:
    """Structured benchmark report."""

    suite_name: str
    generated_at: str
    results: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable benchmark report."""
        latencies = [float(result["latency_ms"]) for result in self.results]
        passed = sum(1 for result in self.results if result.get("passed") is True)
        return {
            "success": True,
            "suite_name": self.suite_name,
            "generated_at": self.generated_at,
            "summary": {
                "case_count": len(self.results),
                "passed": passed,
                "failed": len(self.results) - passed,
                "mean_latency_ms": mean_latency(latencies),
            },
            "results": self.results,
        }


class BenchmarkRunner:
    """Run callable benchmarks and capture latency plus result payloads."""

    def run(
        self,
        name: str,
        benchmark: Callable[[], Any],
        expected: Any | None = None,
        accuracy_hook: Callable[[Any, Any], float] | None = None,
    ) -> dict[str, Any]:
        """Execute a benchmark callable and return a structured result."""
        start = perf_counter()
        result = benchmark()
        elapsed_ms = round((perf_counter() - start) * 1000.0, 3)
        accuracy = None
        passed = True
        if expected is not None:
            accuracy = accuracy_hook(expected, result) if accuracy_hook else self._default_accuracy(expected, result)
            passed = accuracy == 1.0
        return {
            "success": True,
            "name": name,
            "latency_ms": elapsed_ms,
            "accuracy": accuracy,
            "passed": passed,
            "result": result,
        }

    def run_suite(
        self,
        suite_name: str,
        cases: list[BenchmarkCase],
        accuracy_hook: Callable[[Any, Any], float] | None = None,
    ) -> dict[str, Any]:
        """Run benchmark cases and return a report."""
        report = BenchmarkReport(
            suite_name=suite_name,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        for case in cases:
            report.results.append(
                self.run(case.name, case.runner, expected=case.expected, accuracy_hook=accuracy_hook)
            )
        return report.to_dict()

    def _default_accuracy(self, expected: Any, actual: Any) -> float:
        """Return exact-match accuracy for scalar or list outputs."""
        if isinstance(expected, list) and isinstance(actual, list):
            return accuracy_score(expected, actual)
        return 1.0 if expected == actual else 0.0
