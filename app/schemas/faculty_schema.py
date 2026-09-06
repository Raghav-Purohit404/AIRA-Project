"""Faculty ranking and shortlisting API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class CandidateInput(BaseModel):
    """Candidate data accepted by the ranking service."""

    student_id: str
    name: str
    aira_score: float = Field(ge=0.0, le=100.0)
    department: str
    skills: list[str] = Field(default_factory=list)
    cgpa: float = Field(default=0.0, ge=0.0, le=10.0)
    internships: int = Field(default=0, ge=0)
    projects: int = Field(default=0, ge=0)
    hackathons: int = Field(default=0, ge=0)
    semantic_similarity: float | None = Field(default=None, ge=-1.0, le=1.0)


class CandidateFilterRequest(BaseModel):
    """Faculty filtering and pagination request."""

    candidates: list[CandidateInput] | None = None
    department: str | None = None
    skills: list[str] = Field(default_factory=list)
    minimum_cgpa: float | None = Field(default=None, ge=0.0, le=10.0)
    require_all_skills: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def normalize_filters(self) -> "CandidateFilterRequest":
        """Normalize optional text filters."""
        self.department = self.department.strip() if self.department else None
        self.skills = list(dict.fromkeys(skill.strip() for skill in self.skills if skill.strip()))
        return self


class RankedCandidate(BaseModel):
    """Ranked candidate returned to faculty clients."""

    student_id: str
    name: str
    aira_score: float
    rank: int = Field(ge=1)
    department: str
    skills: list[str]
    cgpa: float
    semantic_similarity: float | None = None


class RankingMetadata(BaseModel):
    """Metadata describing ranking, filters, and pagination."""

    total_candidates: int
    filtered_candidates: int
    page: int
    page_size: int
    total_pages: int
    returned: int
    sort: str = "aira_score_desc"
    tie_breakers: list[str] = Field(
        default_factory=lambda: ["cgpa", "internships", "projects", "hackathons", "student_id"]
    )
    semantic_ranking_enabled: bool = False


class ShortlistResponse(BaseModel):
    """Paginated ranking response."""

    success: bool = True
    candidates: list[RankedCandidate]
    metadata: RankingMetadata
