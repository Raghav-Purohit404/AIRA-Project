"""API callable tests for student profile routes."""

from app.api.v1.student_routes import (
    create_student_profile,
    delete_student_profile,
    get_student_profile,
    get_student_profile_summary,
    update_student_profile,
)
from app.schemas.student_schema import StudentProfileCreate, StudentProfileUpdate


def _profile_payload(email: str = "student@example.com") -> StudentProfileCreate:
    """Build a realistic student profile payload."""
    return StudentProfileCreate.model_validate(
        {
            "basic_info": {
                "full_name": "Student One",
                "email": email,
                "department": "Computer Science",
                "batch_year": 2026,
            },
            "academic": {
                "degree": "B.Tech",
                "department": "Computer Science",
                "graduation_year": 2026,
                "cgpa": 8.4,
                "semesters": [{"semester": 1, "sgpa": 8.0, "credits": 20}],
            },
            "skills": [{"name": "Python", "level": "advanced"}],
            "projects": [{"title": "AIRA", "description": "Recruitment intelligence platform", "technologies": ["FastAPI"]}],
            "internships": [{"company": "Acme", "role": "Backend Intern", "start_date": "2025-01-01"}],
            "hackathons": [{"name": "Smart India Hackathon"}],
            "achievements": [{"title": "Department Topper", "category": "academic"}],
        }
    )


def test_student_profile_crud_flow() -> None:
    """Student routes should create, read, update, summarize, and delete profiles."""
    created = create_student_profile(_profile_payload())
    profile_id = created.profile.id

    fetched = get_student_profile(profile_id)
    assert fetched.profile.basic_info.email == "student@example.com"

    updated = update_student_profile(
        profile_id,
        StudentProfileUpdate(skills=[{"name": "Python", "level": "expert"}, {"name": "SQL"}]),
    )
    assert len(updated.profile.skills) == 2

    summary = get_student_profile_summary(profile_id)
    assert summary.summary["skills_count"] == 2

    deleted = delete_student_profile(profile_id)
    assert deleted.deleted_id == profile_id
