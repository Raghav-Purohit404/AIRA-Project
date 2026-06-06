"""Faculty-facing ranking and shortlisting routes."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.schemas.faculty_schema import CandidateFilterRequest, CandidateInput, ShortlistResponse
from app.services.aira.aira_engine import aira_engine
from app.services.ranking.ranking_service import ranking_service
from app.services.student_profile_service import student_profile_service

router = APIRouter()


def _stored_candidates(required_skills: list[str] | None = None) -> list[CandidateInput]:
    """Score stored profiles and convert them into ranking candidates."""
    candidates: list[CandidateInput] = []
    for profile in student_profile_service.list_profiles():
        score = aira_engine.score_profile(profile, required_skills)
        candidates.append(
            CandidateInput(
                student_id=profile.id,
                name=profile.basic_info.full_name,
                aira_score=score.breakdown.final_score,
                department=profile.basic_info.department,
                skills=profile.skill_names(),
                cgpa=profile.academic.cgpa,
                internships=len(profile.internships),
                projects=len(profile.projects),
                hackathons=len(profile.hackathons),
            )
        )
    return candidates


@router.get("/shortlist", response_model=ShortlistResponse)
def get_shortlist(
    department: str | None = None,
    skills: list[str] = Query(default_factory=list),
    minimum_cgpa: float | None = Query(default=None, ge=0.0, le=10.0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ShortlistResponse:
    """Return a filtered, paginated shortlist of stored students."""
    filters = CandidateFilterRequest(
        department=department,
        skills=skills,
        minimum_cgpa=minimum_cgpa,
        page=page,
        page_size=page_size,
    )
    return ranking_service.rank(_stored_candidates(skills), filters)


@router.get("/top-candidates", response_model=ShortlistResponse)
def get_top_candidates(
    limit: int = Query(default=10, ge=1, le=100),
    department: str | None = None,
    skills: list[str] = Query(default_factory=list),
    minimum_cgpa: float | None = Query(default=None, ge=0.0, le=10.0),
) -> ShortlistResponse:
    """Return the Top-N stored candidates."""
    filters = CandidateFilterRequest(
        department=department,
        skills=skills,
        minimum_cgpa=minimum_cgpa,
    )
    return ranking_service.top_candidates(_stored_candidates(skills), limit, filters)


@router.post("/filter", response_model=ShortlistResponse)
def filter_candidates(payload: CandidateFilterRequest) -> ShortlistResponse:
    """Rank supplied candidates or, when omitted, current stored profiles."""
    candidates = payload.candidates or _stored_candidates(payload.skills)
    return ranking_service.rank(candidates, payload)
