"""API schemas for AIRA scoring."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.aira_score import AIRAScore
from app.models.student_profile import StudentProfile


class ScoreProfileRequest(BaseModel):
    """Request payload for scoring a profile directly."""

    profile: StudentProfile
    required_skills: list[str] = Field(default_factory=list)
    ats_weight: float = Field(default=0.0, ge=0.0, le=1.0)


class ScoreStoredProfileRequest(BaseModel):
    """Request payload for scoring a stored profile."""

    required_skills: list[str] = Field(default_factory=list)
    ats_weight: float = Field(default=0.0, ge=0.0, le=1.0)


class ScoreResponse(BaseModel):
    """Structured scoring response."""

    success: bool = True
    score: AIRAScore
    breakdown: dict[str, object]
