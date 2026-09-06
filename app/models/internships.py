"""Internship domain models."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.constants import CANONICAL_SKILL_ALIASES


class Internship(BaseModel):
    """Professional internship experience."""

    company: str = Field(min_length=2, max_length=160)
    role: str = Field(min_length=2, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    start_date: date
    end_date: date | None = None
    description: str = Field(default="", max_length=2000)
    technologies: list[str] = Field(default_factory=list)

    @field_validator("technologies")
    @classmethod
    def normalize_technologies(cls, values: list[str]) -> list[str]:
        """Canonicalize technology aliases for matching and resume projection."""
        result: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = " ".join(value.strip().split())
            item = CANONICAL_SKILL_ALIASES.get(item.casefold(), item)
            if item and item.casefold() not in seen:
                seen.add(item.casefold())
                result.append(item)
        return result

    @model_validator(mode="after")
    def validate_dates(self) -> "Internship":
        """Ensure internship end date is not before start date."""
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("Internship end date must be after start date.")
        return self
