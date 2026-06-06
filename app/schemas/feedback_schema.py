"""API schemas for deterministic feedback."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.student_profile import StudentProfile


class FeedbackRequest(BaseModel):
    """Request payload for generating feedback from a profile."""

    profile: StudentProfile
    target_skills: list[str] = Field(default_factory=list)


class StoredFeedbackRequest(BaseModel):
    """Request payload for stored profile feedback."""

    target_skills: list[str] = Field(default_factory=list)


class FeedbackResponse(BaseModel):
    """Structured feedback response."""

    success: bool = True
    feedback: dict[str, list[str]]
