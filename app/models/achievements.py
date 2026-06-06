"""Achievement domain models."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class AchievementType(StrEnum):
    """Supported achievement categories."""

    ACADEMIC = "academic"
    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    CERTIFICATION = "certification"
    OTHER = "other"


class Achievement(BaseModel):
    """Student achievement or recognition."""

    title: str = Field(min_length=2, max_length=160)
    category: AchievementType = AchievementType.OTHER
    issuer: str | None = Field(default=None, max_length=160)
    awarded_on: date | None = None
    description: str | None = Field(default=None, max_length=1000)
