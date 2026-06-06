"""Cohort-level statistical helpers."""

from __future__ import annotations

from statistics import mean, median, pstdev
from typing import Any


def calculate_percentile(values: list[float], value: float) -> float:
    """Return the percentile rank of a value within a list."""
    if not values:
        return 0.0
    below_or_equal = sum(1 for item in values if item <= value)
    return round((below_or_equal / len(values)) * 100.0, 2)


def summarize_scores(scores: list[float]) -> dict[str, float]:
    """Return descriptive statistics for a score cohort."""
    if not scores:
        return {"count": 0.0, "mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "std_dev": 0.0}
    return {
        "count": float(len(scores)),
        "mean": round(mean(scores), 2),
        "median": round(median(scores), 2),
        "min": round(min(scores), 2),
        "max": round(max(scores), 2),
        "std_dev": round(pstdev(scores), 2),
    }


def score_distribution(scores: list[float]) -> dict[str, int]:
    """Bucket scores into readiness bands."""
    distribution = {"0-39": 0, "40-54": 0, "55-69": 0, "70-84": 0, "85-100": 0}
    for score in scores:
        if score < 40:
            distribution["0-39"] += 1
        elif score < 55:
            distribution["40-54"] += 1
        elif score < 70:
            distribution["55-69"] += 1
        elif score < 85:
            distribution["70-84"] += 1
        else:
            distribution["85-100"] += 1
    return distribution


def rank_by_department(students: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Rank students within each department by score."""
    departments: dict[str, list[dict[str, Any]]] = {}
    for student in students:
        departments.setdefault(str(student.get("department", "unknown")), []).append(student)

    ranked: dict[str, list[dict[str, Any]]] = {}
    for department, department_students in departments.items():
        sorted_students = sorted(department_students, key=lambda item: float(item.get("score", 0)), reverse=True)
        ranked[department] = [{**student, "department_rank": index} for index, student in enumerate(sorted_students, start=1)]
    return ranked
