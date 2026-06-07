"""Certification domain models."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator


class Certification(BaseModel):
    """A student certification or verified credential."""

    name: str = Field(min_length=2, max_length=160)
    issuer: str = Field(min_length=2, max_length=160)
    issue_date: date | None = None
    expiry_date: date | None = None
    credential_id: str | None = Field(default=None, max_length=160)
    credential_url: str | None = Field(default=None, max_length=500)

    @field_validator("name", "issuer", "credential_id", "credential_url")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        """Normalize optional text values."""
        if value is None:
            return None
        return " ".join(value.strip().split())
