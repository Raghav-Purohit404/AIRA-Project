from app.services.analytics.analytics_service import (
    generate_student_insights
)


def test_analytics_service():

    student = {

        "name": "AnalyticsTester",

        "cgpa": 8.6,

        "projects": 4,

        "internships": 2,

        "hackathons": 1,

        "skills": [
            "Python",
            "FastAPI"
        ],

        "semester_scores": [
            7.2,
            7.8,
            8.2,
            8.6
        ]
    }

    result = generate_student_insights(
        student
    )

    assert result["status"] == "success"

    assert "analytics" in result