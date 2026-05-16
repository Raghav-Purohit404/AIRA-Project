# placeholder
from app.services.feedback.feedback_engine import (
    generate_complete_feedback
)


def generate_student_insights(student):

    insights = generate_complete_feedback(
        student
    )

    return {
        "status": "success",
        "analytics": insights
    }


if __name__ == "__main__":

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

    print(result)