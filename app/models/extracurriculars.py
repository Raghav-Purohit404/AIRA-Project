"""Extracurricular activity models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class ActivityType(str, StrEnum):
    """Supported extracurricular activity categories."""

    CLUB = "club"
    SPORTS = "sports"
    VOLUNTEERING = "volunteering"
    CULTURAL = "cultural"
    LEADERSHIP = "leadership"
    OTHER = "other"


class ExtracurricularActivity(BaseModel):
    """Student extracurricular involvement."""

    activity_type: ActivityType = ActivityType.OTHER
    title: str = Field(min_length=2, max_length=160)
    leadership_role: str | None = Field(default=None, max_length=120)
    duration_months: int = Field(default=0, ge=0, le=120)
    achievements: list[str] = Field(default_factory=list)

    @field_validator("title", "leadership_role")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        """Normalize display text."""
        if value is None:
            return None
        return " ".join(value.strip().split())

    @field_validator("achievements")
    @classmethod
    def normalize_achievements(cls, values: list[str]) -> list[str]:
        """Normalize and deduplicate achievements."""
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = " ".join(value.strip().split())
            key = item.casefold()
            if item and key not in seen:
                seen.add(key)
                result.append(item)
        return result
