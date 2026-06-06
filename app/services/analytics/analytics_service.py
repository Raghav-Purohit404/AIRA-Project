"""Facade service for non-LLM analytics features."""

from __future__ import annotations

from typing import Any

from app.services.analytics.cohort_stats import calculate_percentile, rank_by_department, score_distribution, summarize_scores
from app.services.analytics.comparison_engine import compare_against_cohort, compare_students, placement_readiness, skill_distribution
from app.services.analytics.trend_analysis import calculate_trend, improvement_indicators


class AnalyticsService:
    """Coordinate analytics calculations over in-memory profile data."""

    def cohort_statistics(self, students: list[dict[str, Any]]) -> dict[str, Any]:
        """Return cohort summary statistics and per-student percentiles."""
        scores = [float(student.get("score", 0) or 0) for student in students]
        return {
            "success": True,
            "statistics": summarize_scores(scores),
            "score_distribution": score_distribution(scores),
            "department_rankings": rank_by_department(students),
            "skill_distribution": skill_distribution(students),
            "percentiles": [
                {
                    "student_id": student.get("student_id") or student.get("candidate_id"),
                    "percentile": calculate_percentile(scores, float(student.get("score", 0) or 0)),
                }
                for student in students
            ],
        }

    def compare_students(self, primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
        """Return a structured comparison between two students."""
        return {"success": True, "comparison": compare_students(primary, secondary)}

    def compare_to_cohort(self, student: dict[str, Any], cohort: list[dict[str, Any]]) -> dict[str, Any]:
        """Return a structured comparison between one student and a cohort."""
        return {"success": True, "comparison": compare_against_cohort(student, cohort)}

    def trend(self, points: list[dict[str, Any]]) -> dict[str, Any]:
        """Return trend analysis for score points."""
        return {"success": True, "trend": calculate_trend(points), "indicators": improvement_indicators(points)}

    def placement_readiness(self, score: float) -> dict[str, Any]:
        """Return placement readiness analytics."""
        return {"success": True, "readiness": placement_readiness(score)}
