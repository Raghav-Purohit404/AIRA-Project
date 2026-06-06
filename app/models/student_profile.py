"""Student profile aggregate domain model."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

from app.models.academic import AcademicRecord
from app.models.achievements import Achievement
from app.models.hackathons import Hackathon
from app.models.internships import Internship
from app.models.projects import Project
from app.models.skills import Skill


class StudentBasicInfo(BaseModel):
    """Basic student identity and contact information."""

    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    phone: str | None = Field(default=None, max_length=30)
    department: str = Field(min_length=2, max_length=120)
    batch_year: int = Field(ge=2000, le=2100)

    @field_validator("full_name", "department")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        """Normalize display text."""
        return " ".join(value.strip().split())

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email addresses."""
        return value.strip().lower()


class StudentProfile(BaseModel):
    """Complete student profile used across AIRA pipelines."""

    id: str = Field(min_length=1, max_length=80)
    basic_info: StudentBasicInfo
    academic: AcademicRecord
    skills: list[Skill] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    internships: list[Internship] = Field(default_factory=list)
    hackathons: list[Hackathon] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def completeness_score(self) -> float:
        """Calculate profile completeness on a 0-100 scale."""
        checks = [
            bool(self.basic_info.full_name),
            bool(self.basic_info.email),
            bool(self.academic.cgpa >= 0),
            bool(self.academic.semesters),
            bool(self.skills),
            bool(self.projects),
            bool(self.internships),
            bool(self.hackathons),
            bool(self.achievements),
        ]
        return round((sum(checks) / len(checks)) * 100.0, 2)

    def skill_names(self) -> list[str]:
        """Return skill names for scoring and matching services."""
        return [skill.name for skill in self.skills]

    def to_summary(self) -> dict[str, object]:
        """Return a compact serialized profile summary."""
        return {
            "id": self.id,
            "full_name": self.basic_info.full_name,
            "email": self.basic_info.email,
            "department": self.basic_info.department,
            "cgpa": self.academic.cgpa,
            "skills_count": len(self.skills),
            "projects_count": len(self.projects),
            "internships_count": len(self.internships),
            "hackathons_count": len(self.hackathons),
            "achievements_count": len(self.achievements),
            "completeness_score": self.completeness_score(),
        }
