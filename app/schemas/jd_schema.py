"""Job description request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.jd import JobDescription


class JDParseRequest(BaseModel):
    """Request body for parsing a raw job description."""

    text: str = Field(min_length=20, max_length=20000)


class JDParseResponse(BaseModel):
    """Parsed job description response."""

    success: bool = True
    job_description: JobDescription


class JDSkillMapRequest(BaseModel):
    """Request body for normalizing JD skills."""

    skills: list[str] = Field(default_factory=list)


class JDSkillMapResponse(BaseModel):
    """Normalized skill mapping response."""

    success: bool = True
    normalized_skills: list[str]
    categories: dict[str, list[str]]
