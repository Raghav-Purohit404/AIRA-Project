"""Skill domain models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from app.core.constants import CANONICAL_SKILL_ALIASES


class SkillLevel(StrEnum):
    """Supported skill proficiency levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """A student skill with optional proficiency metadata."""

    name: str = Field(min_length=2, max_length=64)
    level: SkillLevel = SkillLevel.INTERMEDIATE
    years_experience: float = Field(default=0.0, ge=0.0, le=20.0)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        """Normalize skill names."""
        normalized = " ".join(value.strip().split())
        return CANONICAL_SKILL_ALIASES.get(normalized.casefold(), normalized)
