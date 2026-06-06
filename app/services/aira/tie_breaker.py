"""Tie-breaking utilities for candidates with equal or near-equal scores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TieBreakCandidate:
    """Candidate fields used by the tie-breaker."""

    candidate_id: str
    score: float
    cgpa: float
    internships: int = 0
    projects: int = 0
    hackathons: int = 0


def _sort_key(candidate: TieBreakCandidate) -> tuple[float, float, int, int, int, str]:
    """Return the priority tuple for descending candidate ordering."""
    return (
        candidate.score,
        candidate.cgpa,
        candidate.internships,
        candidate.projects,
        candidate.hackathons,
        candidate.candidate_id,
    )


def break_ties(candidates: list[TieBreakCandidate]) -> list[TieBreakCandidate]:
    """Sort candidates by score and configured tie-break priority."""
    return sorted(candidates, key=_sort_key, reverse=True)


def rank_candidate_dicts(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank JSON-like candidate dictionaries and add one-based rank values."""
    typed_candidates = [
        TieBreakCandidate(
            candidate_id=str(candidate.get("candidate_id", candidate.get("id", ""))),
            score=float(candidate.get("score", 0.0)),
            cgpa=float(candidate.get("cgpa", 0.0)),
            internships=int(candidate.get("internships", 0)),
            projects=int(candidate.get("projects", 0)),
            hackathons=int(candidate.get("hackathons", 0)),
        )
        for candidate in candidates
    ]
    sorted_ids = [candidate.candidate_id for candidate in break_ties(typed_candidates)]
    by_id = {str(candidate.get("candidate_id", candidate.get("id", ""))): dict(candidate) for candidate in candidates}
    ranked = []
    for index, candidate_id in enumerate(sorted_ids, start=1):
        item = by_id[candidate_id]
        item["rank"] = index
        ranked.append(item)
    return ranked
