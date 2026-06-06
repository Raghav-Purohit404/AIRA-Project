"""Trend analysis utilities for score time series."""

from __future__ import annotations

from typing import Any


def calculate_trend(points: list[dict[str, Any]]) -> dict[str, Any]:
    """Calculate direction and delta for chronological score points."""
    if len(points) < 2:
        return {"direction": "stable", "delta": 0.0, "points": points}

    ordered_points = sorted(points, key=lambda item: str(item.get("period", "")))
    first_score = float(ordered_points[0].get("score", 0) or 0)
    last_score = float(ordered_points[-1].get("score", 0) or 0)
    delta = round(last_score - first_score, 2)
    if delta > 0:
        direction = "up"
    elif delta < 0:
        direction = "down"
    else:
        direction = "stable"
    return {"direction": direction, "delta": delta, "points": ordered_points}


def moving_average(values: list[float], window_size: int = 3) -> list[float]:
    """Return a simple moving average series."""
    if window_size <= 0:
        raise ValueError("Window size must be greater than zero.")
    averages = []
    for index in range(len(values)):
        window = values[max(0, index - window_size + 1) : index + 1]
        averages.append(round(sum(window) / len(window), 2))
    return averages


def improvement_indicators(points: list[dict[str, Any]]) -> dict[str, object]:
    """Calculate score and profile growth indicators."""
    trend = calculate_trend(points)
    if len(points) < 2:
        completeness_delta = 0.0
    else:
        ordered_points = sorted(points, key=lambda item: str(item.get("period", "")))
        completeness_delta = round(
            float(ordered_points[-1].get("completeness_score", 0) or 0)
            - float(ordered_points[0].get("completeness_score", 0) or 0),
            2,
        )
    return {
        "score_progression": trend,
        "profile_growth": completeness_delta,
        "improving": trend["delta"] > 0 or completeness_delta > 0,
    }
