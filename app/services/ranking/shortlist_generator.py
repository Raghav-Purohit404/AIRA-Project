"""High-level shortlist generation helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.schemas.faculty_schema import CandidateFilterRequest, CandidateInput, ShortlistResponse
from app.services.ranking.ranking_service import RankingService


class ShortlistGenerator:
    """Generate Top-N candidate shortlists with optional constraints."""

    def __init__(self, ranking_service: RankingService | None = None) -> None:
        self.ranking_service = ranking_service or RankingService()

    def generate(
        self,
        candidates: list[CandidateInput | dict[str, Any]],
        *,
        limit: int = 10,
        minimum_score: float | None = None,
        department_cap: int | None = None,
        filters: CandidateFilterRequest | None = None,
    ) -> ShortlistResponse:
        """Return a constrained Top-N shortlist."""
        normalized = [
            candidate if isinstance(candidate, CandidateInput) else CandidateInput.model_validate(candidate)
            for candidate in candidates
        ]
        if minimum_score is not None:
            normalized = [candidate for candidate in normalized if candidate.aira_score >= minimum_score]
        ranked = self.ranking_service.top_candidates(normalized, limit=max(limit, 1), filters=filters)
        if department_cap is None:
            return ranked
        selected = []
        department_counts: Counter[str] = Counter()
        for candidate in ranked.candidates:
            if department_counts[candidate.department] >= department_cap:
                continue
            department_counts[candidate.department] += 1
            selected.append(candidate)
        ranked.candidates = selected
        ranked.metadata.returned = len(selected)
        return ranked


shortlist_generator = ShortlistGenerator()
