"""Feedback domain models."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SkillGap(BaseModel):
    """A missing or weak skill identified during feedback generation."""

    skill: str = Field(min_length=1, max_length=120)
    priority: str = Field(default="medium", pattern=r"^(low|medium|high)$")
    recommendation: str = Field(min_length=2, max_length=500)


class FeedbackSummary(BaseModel):
    """Structured student feedback returned by AI or rule engines."""

    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    skill_gaps: list[SkillGap] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
