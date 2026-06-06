"""AIRA score domain models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AIRAScoreBreakdown(BaseModel):
    """Weighted score components for one student profile."""

    cgpa_score: float = Field(ge=0.0)
    skill_score: float = Field(ge=0.0)
    project_score: float = Field(ge=0.0)
    internship_score: float = Field(ge=0.0)
    hackathon_score: float = Field(ge=0.0)
    achievement_score: float = Field(ge=0.0)
    final_score: float = Field(ge=0.0)


class AIRAScore(BaseModel):
    """Complete AIRA score record."""

    student_id: str
    breakdown: AIRAScoreBreakdown
    normalized_inputs: dict[str, float]
    readiness_level: str

    def to_flat_dict(self) -> dict[str, object]:
        """Return the expected flat score structure."""
        return {
            **self.breakdown.model_dump(),
            "student_id": self.student_id,
            "readiness_level": self.readiness_level,
            "normalized_inputs": self.normalized_inputs,
        }
