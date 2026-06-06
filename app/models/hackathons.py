"""Hackathon domain models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Hackathon(BaseModel):
    """Hackathon participation record."""

    name: str = Field(min_length=2, max_length=160)
    organizer: str | None = Field(default=None, max_length=160)
    position: str | None = Field(default=None, max_length=120)
    project_title: str | None = Field(default=None, max_length=160)
    technologies: list[str] = Field(default_factory=list)
