"""In-memory student profile service.

The service owns persistence concerns for the current phase. Replacing this
with PostgreSQL later should not require route or scoring changes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status

from app.models.student_profile import StudentProfile
from app.schemas.student_schema import StudentProfileCreate, StudentProfileUpdate


class StudentProfileService:
    """Manage student profiles in memory."""

    def __init__(self) -> None:
        self._profiles: dict[str, StudentProfile] = {}

    def create_profile(self, payload: StudentProfileCreate) -> StudentProfile:
        """Create and store a student profile."""
        profile_id = str(uuid4())
        profile = StudentProfile(id=profile_id, **payload.model_dump())
        self._profiles[profile_id] = profile
        return profile

    def get_profile(self, profile_id: str) -> StudentProfile:
        """Return a profile by identifier."""
        profile = self._profiles.get(profile_id)
        if profile is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")
        return profile

    def update_profile(self, profile_id: str, payload: StudentProfileUpdate) -> StudentProfile:
        """Update a profile by identifier."""
        existing = self.get_profile(profile_id)
        updates = payload.model_dump(exclude_unset=True)
        updated = existing.model_copy(update={**updates, "updated_at": datetime.now(timezone.utc)}, deep=True)
        self._profiles[profile_id] = updated
        return updated

    def delete_profile(self, profile_id: str) -> str:
        """Delete a profile by identifier."""
        self.get_profile(profile_id)
        del self._profiles[profile_id]
        return profile_id

    def list_profiles(self) -> list[StudentProfile]:
        """Return all stored profiles."""
        return list(self._profiles.values())


student_profile_service = StudentProfileService()
