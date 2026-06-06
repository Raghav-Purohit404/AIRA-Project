<<<<<<< HEAD
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
=======
from app.services.feedback.feedback_engine import (
    generate_complete_feedback
)


def test_feedback_generation():

    student = {

        "name": "TestStudent",

        "cgpa": 8.2,

        "projects": 3,

        "internships": 1,

        "hackathons": 0,

        "skills": [
            "Python",
            "Docker"
        ],

        "semester_scores": [
            7.1,
            7.5,
            8.0,
            8.2
        ]
    }

    result = generate_complete_feedback(
        student
    )

    assert "comparison" in result

    assert "trend_analysis" in result

    assert "ranking" in result

    assert "suggestions" in result
>>>>>>> 6f50f52c80d4b77411b7a82311c9bf3403b4fd7e
