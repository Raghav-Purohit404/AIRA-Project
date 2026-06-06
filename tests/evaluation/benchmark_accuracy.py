"""Evaluation smoke test for benchmark accuracy metrics."""

from app.services.benchmark.evaluation_metrics import (
    accuracy_score,
    f1_score,
    mean_reciprocal_rank,
    precision_score,
    recall_score,
)


def test_accuracy_score() -> None:
    """Accuracy should count aligned exact matches."""
    assert accuracy_score(["a", "b", "c"], ["a", "x", "c"]) == 0.6667


def test_classification_metrics() -> None:
    """Precision, recall, and F1 should use set overlap."""
    expected = ["python", "sql"]
    actual = ["python", "react"]

    assert precision_score(expected, actual) == 0.5
    assert recall_score(expected, actual) == 0.5
    assert f1_score(expected, actual) == 0.5


def test_ranking_quality_metric() -> None:
    """MRR should reward earlier relevant ranked items."""
    assert mean_reciprocal_rank(["c"], ["a", "b", "c"]) == 0.3333
