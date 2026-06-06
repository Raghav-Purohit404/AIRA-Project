"""Evaluation metrics for benchmark reports."""

from __future__ import annotations


def accuracy_score(expected: list[object], actual: list[object]) -> float:
    """Return exact-match accuracy for aligned expected and actual values."""
    if not expected:
        return 0.0
    if len(actual) < len(expected):
        raise ValueError("Actual results must include at least as many items as expected results.")
    matches = sum(1 for expected_item, actual_item in zip(expected, actual) if expected_item == actual_item)
    return round(matches / len(expected), 4)


def mean_latency(latencies_ms: list[float]) -> float:
    """Return average latency in milliseconds."""
    if not latencies_ms:
        return 0.0
    return round(sum(latencies_ms) / len(latencies_ms), 3)


def precision_score(expected: list[object], actual: list[object]) -> float:
    """Return set-based precision for predicted or retrieved items."""
    actual_set = set(actual)
    if not actual_set:
        return 0.0
    expected_set = set(expected)
    return round(len(expected_set.intersection(actual_set)) / len(actual_set), 4)


def recall_score(expected: list[object], actual: list[object]) -> float:
    """Return set-based recall for predicted or retrieved items."""
    expected_set = set(expected)
    if not expected_set:
        return 0.0
    actual_set = set(actual)
    return round(len(expected_set.intersection(actual_set)) / len(expected_set), 4)


def f1_score(expected: list[object], actual: list[object]) -> float:
    """Return the harmonic mean of precision and recall."""
    precision = precision_score(expected, actual)
    recall = recall_score(expected, actual)
    if precision + recall == 0:
        return 0.0
    return round((2 * precision * recall) / (precision + recall), 4)


def mean_reciprocal_rank(relevant_items: list[object], ranked_items: list[object]) -> float:
    """Return reciprocal rank for the first relevant ranked item."""
    relevant_set = set(relevant_items)
    if not relevant_set:
        return 0.0
    for index, item in enumerate(ranked_items, start=1):
        if item in relevant_set:
            return round(1 / index, 4)
    return 0.0


def precision_at_k(relevant_items: list[object], ranked_items: list[object], k: int) -> float:
    """Return precision at rank k."""
    if k <= 0:
        raise ValueError("k must be greater than zero.")
    return precision_score(relevant_items, ranked_items[:k])


def recall_at_k(relevant_items: list[object], ranked_items: list[object], k: int) -> float:
    """Return recall at rank k."""
    if k <= 0:
        raise ValueError("k must be greater than zero.")
    return recall_score(relevant_items, ranked_items[:k])
