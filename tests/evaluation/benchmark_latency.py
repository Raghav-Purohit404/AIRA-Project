"""Evaluation smoke test for benchmark latency metrics."""

from app.services.benchmark.evaluation_metrics import mean_latency
from app.services.benchmark.benchmark_runner import BenchmarkCase, BenchmarkRunner


def test_mean_latency() -> None:
    """Mean latency should average millisecond values."""
    assert mean_latency([10.0, 20.0, 30.0]) == 20.0


def test_benchmark_runner_generates_report() -> None:
    """Benchmark runner should execute cases and summarize report results."""
    report = BenchmarkRunner().run_suite(
        "demo",
        [BenchmarkCase(name="case", runner=lambda: ["a", "b"], expected=["a", "b"])],
    )

    assert report["success"] is True
    assert report["summary"]["case_count"] == 1
    assert report["summary"]["passed"] == 1
