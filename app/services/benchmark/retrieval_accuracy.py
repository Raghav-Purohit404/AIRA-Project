"""Retrieval relevance benchmark utilities."""

from __future__ import annotations

from typing import Any

from app.services.benchmark.evaluation_metrics import mean_reciprocal_rank
from app.services.similarity.similarity_service import SimilarityService


class RetrievalAccuracyBenchmark:
    """Evaluate Top-K retrieval relevance."""

    def __init__(self, similarity_service: SimilarityService | None = None) -> None:
        self.similarity_service = similarity_service or SimilarityService()

    def run(self, cases: list[dict[str, Any]] | None = None, k: int = 5) -> dict[str, Any]:
        """Run retrieval cases and calculate MRR."""
        samples = cases or [
            {
                "query": "python backend",
                "relevant": ["doc-1"],
                "documents": [
                    {"id": "doc-1", "text": "Python backend API development"},
                    {"id": "doc-2", "text": "Graphic design portfolio"},
                ],
            }
        ]
        results: list[dict[str, Any]] = []
        for index, case in enumerate(samples, start=1):
            retrieved = self.similarity_service.top_k(str(case["query"]), case["documents"], k=k)
            ranked_ids = [str(item["id"]) for item in retrieved]
            mrr = mean_reciprocal_rank([str(item) for item in case.get("relevant", [])], ranked_ids)
            results.append({"case": index, "ranked_ids": ranked_ids, "mrr": mrr, "passed": mrr > 0.0})
        return {
            "success": all(result["passed"] for result in results),
            "benchmark": "retrieval_accuracy",
            "summary": {"case_count": len(results)},
            "results": results,
        }


retrieval_accuracy_benchmark = RetrievalAccuracyBenchmark()
