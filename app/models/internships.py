"""Internship domain models."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, model_validator


class Internship(BaseModel):
    """Professional internship experience."""

    company: str = Field(min_length=2, max_length=160)
    role: str = Field(min_length=2, max_length=160)
    start_date: date
    end_date: date | None = None
    description: str = Field(default="", max_length=2000)
    technologies: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "Internship":
        """Ensure internship end date is not before start date."""
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("Internship end date must be after start date.")
        return self
