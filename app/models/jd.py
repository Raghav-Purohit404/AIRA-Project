"""Job description domain models."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class JobDescription(BaseModel):
    """Structured representation of a parsed job description."""

    role_title: str = Field(min_length=2, max_length=160)
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    education_requirements: list[str] = Field(default_factory=list)
    experience_requirements: list[str] = Field(default_factory=list)
    extracted_keywords: list[str] = Field(default_factory=list)
    raw_text: str | None = Field(default=None, max_length=10000)

    @field_validator(
        "required_skills",
        "preferred_skills",
        "education_requirements",
        "experience_requirements",
        "extracted_keywords",
    )
    @classmethod
    def normalize_list(cls, values: list[str]) -> list[str]:
        """Normalize and deduplicate text lists."""
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = " ".join(value.strip().split())
            key = item.casefold()
            if item and key not in seen:
                seen.add(key)
                result.append(item)
        return result
