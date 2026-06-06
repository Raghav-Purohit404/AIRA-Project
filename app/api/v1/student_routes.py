from fastapi import APIRouter

from app.schemas.student_schema import (
    StudentProfileCreate,
    StudentProfileDeleteResponse,
    StudentProfileResponse,
    StudentProfileSummaryResponse,
    StudentProfileUpdate,
)
from app.services.student_profile_service import student_profile_service

router = APIRouter()


@router.post("/profile", response_model=StudentProfileResponse)
def create_student_profile(payload: StudentProfileCreate) -> StudentProfileResponse:
    """Create a student profile."""
    profile = student_profile_service.create_profile(payload)
    return StudentProfileResponse(profile=profile, completeness_score=profile.completeness_score())


@router.get("/profile/{profile_id}", response_model=StudentProfileResponse)
def get_student_profile(profile_id: str) -> StudentProfileResponse:
    """Get a student profile."""
    profile = student_profile_service.get_profile(profile_id)
    return StudentProfileResponse(profile=profile, completeness_score=profile.completeness_score())


@router.put("/profile/{profile_id}", response_model=StudentProfileResponse)
def update_student_profile(profile_id: str, payload: StudentProfileUpdate) -> StudentProfileResponse:
    """Update a student profile."""
    profile = student_profile_service.update_profile(profile_id, payload)
    return StudentProfileResponse(profile=profile, completeness_score=profile.completeness_score())


@router.delete("/profile/{profile_id}", response_model=StudentProfileDeleteResponse)
def delete_student_profile(profile_id: str) -> StudentProfileDeleteResponse:
    """Delete a student profile."""
    deleted_id = student_profile_service.delete_profile(profile_id)
    return StudentProfileDeleteResponse(deleted_id=deleted_id)


@router.get("/profile/{profile_id}/summary", response_model=StudentProfileSummaryResponse)
def get_student_profile_summary(profile_id: str) -> StudentProfileSummaryResponse:
    """Get a compact profile summary."""
    profile = student_profile_service.get_profile(profile_id)
    return StudentProfileSummaryResponse(summary=profile.to_summary())
