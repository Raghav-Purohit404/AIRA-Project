"""Research publication domain model for resume projection."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Publication(BaseModel):
    """A candidate-authored research output supported by validated profile data."""

    title: str = Field(min_length=2, max_length=300)
    authors: list[str] = Field(default_factory=list)
    venue: str | None = Field(default=None, max_length=240)
    year: int | None = Field(default=None, ge=1900, le=2100)
    doi: str | None = Field(default=None, max_length=300)
    url: str | None = Field(default=None, max_length=500)

    @field_validator("title", "venue", "doi", "url")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        return " ".join(value.strip().split()) if value else None

    @field_validator("authors")
    @classmethod
    def normalize_authors(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(" ".join(value.strip().split()) for value in values if value.strip()))
