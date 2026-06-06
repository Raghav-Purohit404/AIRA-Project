"""Feedback service facade."""

from __future__ import annotations

from typing import Any

from app.models.student_profile import StudentProfile
from app.services.feedback.rule_feedback import generate_profile_feedback, generate_rule_feedback


class FeedbackEngine:
    """Generate deterministic feedback without LLM dependencies."""

    def generate(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Return structured strengths, weaknesses, and recommendations."""
        feedback = generate_rule_feedback(profile)
        return {"success": True, "feedback": feedback}

    def generate_for_profile(self, profile: StudentProfile, target_skills: list[str] | None = None) -> dict[str, Any]:
        """Return deterministic feedback for a full student profile."""
        feedback = generate_profile_feedback(profile.model_dump(mode="json"), target_skills)
        return {"success": True, "feedback": feedback}
