"""Candidate ranking and shortlist generation."""

from __future__ import annotations

from collections.abc import Iterable
from math import ceil

from app.schemas.faculty_schema import (
    CandidateFilterRequest,
    CandidateInput,
    RankedCandidate,
    RankingMetadata,
    ShortlistResponse,
)


class RankingService:
    """Rank AIRA-scored candidates with deterministic tie-break rules."""

    def rank(
        self,
        candidates: Iterable[CandidateInput | dict[str, object]],
        filters: CandidateFilterRequest | None = None,
    ) -> ShortlistResponse:
        """Filter, rank, and paginate candidates."""
        request = filters or CandidateFilterRequest()
        normalized = [
            candidate if isinstance(candidate, CandidateInput) else CandidateInput.model_validate(candidate)
            for candidate in candidates
        ]
        filtered = self._apply_filters(normalized, request)
        ordered = sorted(filtered, key=self._sort_key)
        ranked = [self._to_ranked(candidate, rank) for rank, candidate in enumerate(ordered, start=1)]
        start = (request.page - 1) * request.page_size
        page_items = ranked[start : start + request.page_size]
        metadata = RankingMetadata(
            total_candidates=len(normalized),
            filtered_candidates=len(ranked),
            page=request.page,
            page_size=request.page_size,
            total_pages=ceil(len(ranked) / request.page_size) if ranked else 0,
            returned=len(page_items),
            semantic_ranking_enabled=any(candidate.semantic_similarity is not None for candidate in normalized),
        )
        return ShortlistResponse(candidates=page_items, metadata=metadata)

    def top_candidates(
        self,
        candidates: Iterable[CandidateInput | dict[str, object]],
        limit: int = 10,
        filters: CandidateFilterRequest | None = None,
    ) -> ShortlistResponse:
        """Return the highest-ranked candidates up to a bounded limit."""
        bounded_limit = max(1, min(limit, 100))
        request = (filters or CandidateFilterRequest()).model_copy(
            update={"page": 1, "page_size": bounded_limit}
        )
        return self.rank(candidates, request)

    @staticmethod
    def _apply_filters(
        candidates: list[CandidateInput],
        request: CandidateFilterRequest,
    ) -> list[CandidateInput]:
        """Apply department, skill, and CGPA filters."""
        department = request.department.casefold() if request.department else None
        requested_skills = {skill.casefold() for skill in request.skills}
        result: list[CandidateInput] = []
        for candidate in candidates:
            candidate_skills = {skill.casefold() for skill in candidate.skills}
            skill_match = (
                requested_skills.issubset(candidate_skills)
                if request.require_all_skills
                else not requested_skills or bool(requested_skills & candidate_skills)
            )
            if department and candidate.department.casefold() != department:
                continue
            if request.minimum_cgpa is not None and candidate.cgpa < request.minimum_cgpa:
                continue
            if not skill_match:
                continue
            result.append(candidate)
        return result

    @staticmethod
    def _sort_key(candidate: CandidateInput) -> tuple[float, float, int, int, int, float, str]:
        """Return a stable key representing descending priorities."""
        return (
            -candidate.aira_score,
            -candidate.cgpa,
            -candidate.internships,
            -candidate.projects,
            -candidate.hackathons,
            -(candidate.semantic_similarity or 0.0),
            candidate.student_id,
        )

    @staticmethod
    def _to_ranked(candidate: CandidateInput, rank: int) -> RankedCandidate:
        """Convert a candidate into its public ranked representation."""
        return RankedCandidate(
            student_id=candidate.student_id,
            name=candidate.name,
            aira_score=round(candidate.aira_score, 2),
            rank=rank,
            department=candidate.department,
            skills=candidate.skills,
            cgpa=candidate.cgpa,
            semantic_similarity=candidate.semantic_similarity,
        )


ranking_service = RankingService()
