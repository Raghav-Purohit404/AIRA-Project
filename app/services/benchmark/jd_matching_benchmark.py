"""Job-description to profile matching benchmarks."""

from __future__ import annotations

from typing import Any

from app.services.similarity.similarity_service import SimilarityService


class JDMatchingBenchmark:
    """Evaluate JD-profile semantic matching quality."""

    def __init__(self, similarity_service: SimilarityService | None = None) -> None:
        self.similarity_service = similarity_service or SimilarityService()

    def run(self, cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Run matching cases and return relevance scores."""
        samples = cases or [
            {
                "profile": {"skills": ["Python", "FastAPI", "SQL"], "projects": [{"title": "API"}]},
                "job_description": "Backend intern with Python, API, and database skills",
                "minimum_score": 0.05,
            }
        ]
        results: list[dict[str, Any]] = []
        for index, case in enumerate(samples, start=1):
            score = self.similarity_service.match_job_description(case["profile"], str(case["job_description"]))
            passed = score >= float(case.get("minimum_score", 0.0))
            results.append({"case": index, "score": score, "passed": passed})
        return {
            "success": all(result["passed"] for result in results),
            "benchmark": "jd_matching_benchmark",
            "summary": {"case_count": len(results)},
            "results": results,
        }


jd_matching_benchmark = JDMatchingBenchmark()
