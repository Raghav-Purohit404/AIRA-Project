"""Academic domain models for student profiles."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class SemesterRecord(BaseModel):
    """Academic performance for a single semester."""

    semester: int = Field(ge=1, le=12)
    sgpa: float = Field(ge=0.0, le=10.0)
    credits: int = Field(default=0, ge=0, le=40)


class AcademicRecord(BaseModel):
    """Aggregate academic record for a student."""

    degree: str = Field(min_length=2, max_length=120)
    department: str = Field(min_length=2, max_length=120)
    graduation_year: int = Field(ge=2000, le=2100)
    cgpa: float = Field(ge=0.0, le=10.0)
    semesters: list[SemesterRecord] = Field(default_factory=list)

    @field_validator("degree", "department")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        """Normalize display text fields."""
        return " ".join(value.strip().split())

    def semester_count(self) -> int:
        """Return the number of semester records."""
        return len(self.semesters)
