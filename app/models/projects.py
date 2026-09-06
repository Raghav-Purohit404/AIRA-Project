"""Project domain models."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.core.constants import CANONICAL_SKILL_ALIASES


class Project(BaseModel):
    """A portfolio project."""

    title: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=10, max_length=2000)
    technologies: list[str] = Field(default_factory=list)
    role: str | None = Field(default=None, max_length=120)
    outcome: str | None = Field(default=None, max_length=500)
    repository_url: str | None = Field(default=None, max_length=500)
    deployment_url: str | None = Field(default=None, max_length=500)
    date: str | None = Field(default=None, max_length=80)

    @field_validator("title", "description", "role", "outcome", "repository_url", "deployment_url", "date")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        """Normalize optional text fields."""
        if value is None:
            return None
        return " ".join(value.strip().split())

    @field_validator("technologies")
    @classmethod
    def normalize_technologies(cls, values: list[str]) -> list[str]:
        """Normalize and deduplicate technologies."""
        normalized: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = " ".join(value.strip().split())
            item = CANONICAL_SKILL_ALIASES.get(item.casefold(), item)
            if item and item.lower() not in seen:
                seen.add(item.lower())
                normalized.append(item)
        return normalized
