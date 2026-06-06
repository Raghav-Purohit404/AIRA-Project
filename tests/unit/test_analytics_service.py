"""Tests for analytics service facade."""

from app.services.analytics.analytics_service import AnalyticsService


def test_cohort_statistics_include_percentiles() -> None:
    """Cohort statistics should include summary stats and student percentiles."""
    students = [{"student_id": "s1", "score": 50}, {"student_id": "s2", "score": 100}]

    result = AnalyticsService().cohort_statistics(students)

    assert result["success"] is True
    assert result["statistics"]["mean"] == 75.0
    assert result["percentiles"][1]["percentile"] == 100.0


def test_compare_students_identifies_winner() -> None:
    """Comparison should identify the higher score."""
    result = AnalyticsService().compare_students({"student_id": "a", "score": 90}, {"student_id": "b", "score": 80})

    assert result["comparison"]["winner"] == "primary"


def test_empty_cohort_statistics_are_structured() -> None:
    """Empty cohorts should return zeroed statistics without crashing."""
    result = AnalyticsService().cohort_statistics([])

    assert result["statistics"]["count"] == 0.0
    assert result["percentiles"] == []
