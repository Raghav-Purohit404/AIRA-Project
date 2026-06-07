"""Regression suite helpers for benchmark report comparison."""

from __future__ import annotations

from typing import Any

from app.core.constants import BENCHMARK_THRESHOLDS


class RegressionSuite:
    """Detect performance degradation between baseline and current metrics."""

    def compare(self, baseline: dict[str, float], current: dict[str, float]) -> dict[str, Any]:
        """Compare current metrics against a baseline."""
        results: list[dict[str, Any]] = []
        maximum_drift = BENCHMARK_THRESHOLDS["maximum_score_drift"]
        for metric, baseline_value in baseline.items():
            current_value = float(current.get(metric, baseline_value))
            drift = round(current_value - float(baseline_value), 4)
            passed = abs(drift) <= maximum_drift
            results.append(
                {
                    "metric": metric,
                    "baseline": baseline_value,
                    "current": current_value,
                    "drift": drift,
                    "passed": passed,
                }
            )
        return {
            "success": all(result["passed"] for result in results),
            "benchmark": "regression_suite",
            "summary": {"metric_count": len(results), "maximum_drift": maximum_drift},
            "results": results,
        }


regression_suite = RegressionSuite()
