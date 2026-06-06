"""Tests for deterministic feedback generation."""

from app.services.feedback.feedback_engine import FeedbackEngine


def test_feedback_engine_generates_expected_sections() -> None:
    """Feedback should include strengths, weaknesses, and recommendations."""
    result = FeedbackEngine().generate({"cgpa": 9.0, "internships": 0, "projects": 1, "skills": ["Python"]})
    feedback = result["feedback"]

    assert "Strong CGPA" in feedback["strengths"]
    assert "No internships" in feedback["weaknesses"]
    assert "Complete one internship" in feedback["recommendations"]


def test_feedback_engine_detects_strong_profile() -> None:
    """Strong profiles should produce portfolio and skill strengths."""
    result = FeedbackEngine().generate(
        {
            "cgpa": 8.6,
            "internships": 1,
            "projects": 3,
            "skills": ["Python", "FastAPI", "React", "SQL", "Docker"],
        }
    )

    assert "Strong project portfolio" in result["feedback"]["strengths"]
    assert "Broad skill set" in result["feedback"]["strengths"]
