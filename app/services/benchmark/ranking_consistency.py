"""Ranking stability benchmarks."""

from __future__ import annotations

from typing import Any

from app.schemas.faculty_schema import CandidateFilterRequest
from app.services.ranking.ranking_service import RankingService


class RankingConsistencyBenchmark:
    """Verify deterministic ranking across repeated executions."""

    def __init__(self, ranking_service: RankingService | None = None) -> None:
        self.ranking_service = ranking_service or RankingService()

    def run(self, candidates: list[dict[str, Any]] | None = None, iterations: int = 3) -> dict[str, Any]:
        """Run repeated ranking passes and compare ordering."""
        sample_candidates = candidates or [
            {"student_id": "a", "name": "A", "aira_score": 88, "department": "CSE", "skills": ["Python"], "cgpa": 8.5},
            {"student_id": "b", "name": "B", "aira_score": 88, "department": "CSE", "skills": ["Python"], "cgpa": 9.0},
        ]
        orders: list[list[str]] = []
        for _ in range(max(1, iterations)):
            response = self.ranking_service.rank(sample_candidates, CandidateFilterRequest())
            orders.append([candidate.student_id for candidate in response.candidates])
        stable = all(order == orders[0] for order in orders)
        return {
            "success": stable,
            "benchmark": "ranking_consistency",
            "summary": {"iterations": len(orders), "stable": stable},
            "results": [{"order": order} for order in orders],
        }


ranking_consistency_benchmark = RankingConsistencyBenchmark()
