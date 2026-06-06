"""Tests for trend analysis helpers."""

from app.services.analytics.trend_analysis import calculate_trend, moving_average


def test_calculate_trend_detects_upward_direction() -> None:
    """Trend analysis should detect increasing score series."""
    result = calculate_trend([{"period": "2026-01", "score": 70}, {"period": "2026-02", "score": 75}])

    assert result["direction"] == "up"
    assert result["delta"] == 5.0


def test_moving_average_uses_available_window() -> None:
    """Moving average should use partial windows at the beginning."""
    assert moving_average([10, 20, 30], window_size=2) == [10.0, 15.0, 25.0]


def test_calculate_trend_detects_stable_single_point() -> None:
    """Single-point trends should be stable."""
    result = calculate_trend([{"period": "2026-01", "score": 70}])

    assert result["direction"] == "stable"
    assert result["delta"] == 0.0
