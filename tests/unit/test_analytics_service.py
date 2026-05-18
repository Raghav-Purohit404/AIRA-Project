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