"""API schemas for analytics endpoints."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyticsProfileInput(BaseModel):
    """Compact scored student input for analytics."""

    student_id: str
    department: str
    score: float = Field(ge=0.0, le=100.0)
    cgpa: float = Field(ge=0.0, le=10.0)
    skills: list[str] = Field(default_factory=list)
    projects: int = Field(default=0, ge=0)
    internships: int = Field(default=0, ge=0)
    hackathons: int = Field(default=0, ge=0)


class CohortAnalyticsRequest(BaseModel):
    """Request payload for cohort analytics."""

    students: list[AnalyticsProfileInput]


class StudentComparisonRequest(BaseModel):
    """Request payload for comparing two scored students."""

    primary: AnalyticsProfileInput
    secondary: AnalyticsProfileInput


class TrendPoint(BaseModel):
    """Score trend point."""

    period: str
    score: float = Field(ge=0.0, le=100.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=100.0)


class TrendRequest(BaseModel):
    """Request payload for trend analytics."""

    points: list[TrendPoint]


class AnalyticsResponse(BaseModel):
    """Structured analytics response."""

    success: bool = True
    data: dict[str, object]
