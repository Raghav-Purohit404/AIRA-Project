from fastapi import APIRouter

from app.services.analytics.analytics_service import (
    generate_student_insights
)

router = APIRouter()


@router.post("/mock-insights")
def mock_insights():

    sample_student = {

        "name": "BinLad",

        "cgpa": 8.4,

        "projects": 4,

        "internships": 1,

        "hackathons": 0,

        "skills": [
            "Python",
            "FastAPI",
            "Docker"
        ],

        "semester_scores": [
            7.2,
            7.8,
            8.1,
            8.4
        ]
    }

    result = generate_student_insights(
        sample_student
    )

    return result