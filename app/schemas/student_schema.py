"""API schemas for student profile operations."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.student_profile import StudentBasicInfo, StudentProfile
from app.models.academic import AcademicRecord
from app.models.achievements import Achievement
from app.models.hackathons import Hackathon
from app.models.internships import Internship
from app.models.projects import Project
from app.models.skills import Skill
from app.models.certifications import Certification
from app.models.extracurriculars import ExtracurricularActivity
from app.models.publications import Publication


class StudentProfileCreate(BaseModel):
    """Request payload for creating a student profile."""

    basic_info: StudentBasicInfo
    academic: AcademicRecord
    skills: list[Skill] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    internships: list[Internship] = Field(default_factory=list)
    hackathons: list[Hackathon] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    extracurriculars: list[ExtracurricularActivity] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)


class StudentProfileUpdate(BaseModel):
    """Request payload for updating a student profile."""

    basic_info: StudentBasicInfo | None = None
    academic: AcademicRecord | None = None
    skills: list[Skill] | None = None
    projects: list[Project] | None = None
    internships: list[Internship] | None = None
    hackathons: list[Hackathon] | None = None
    achievements: list[Achievement] | None = None
    certifications: list[Certification] | None = None
    extracurriculars: list[ExtracurricularActivity] | None = None
    publications: list[Publication] | None = None


class StudentProfileResponse(BaseModel):
    """Structured student profile response."""

    success: bool = True
    profile: StudentProfile
    completeness_score: float


class StudentProfileDeleteResponse(BaseModel):
    """Structured delete response."""

    success: bool = True
    deleted_id: str


class StudentProfileSummaryResponse(BaseModel):
    """Structured profile summary response."""

    success: bool = True
    summary: dict[str, object]
