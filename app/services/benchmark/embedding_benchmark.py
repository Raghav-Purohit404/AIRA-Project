"""Embedding latency and similarity quality benchmarks."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from app.core.constants import BENCHMARK_THRESHOLDS
from app.services.similarity.similarity_service import SimilarityService


class EmbeddingBenchmark:
    """Evaluate embedding generation and semantic similarity quality."""

    def __init__(self, similarity_service: SimilarityService | None = None) -> None:
        self.similarity_service = similarity_service or SimilarityService()

    def run(self, samples: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Run embedding benchmarks over text pairs."""
        cases = samples or [
            {"a": "Python FastAPI backend", "b": "backend development with Python", "expected_min": 0.05},
            {"a": "database sql postgres", "b": "frontend animation design", "expected_max": 0.95},
        ]
        results: list[dict[str, Any]] = []
        latencies: list[float] = []
        for index, case in enumerate(cases, start=1):
            start = perf_counter()
            score = self.similarity_service.calculate_similarity(str(case["a"]), str(case["b"]))
            latency_ms = round((perf_counter() - start) * 1000.0, 3)
            latencies.append(latency_ms)
            passed = score >= case.get("expected_min", -1.0) and score <= case.get("expected_max", 1.0)
            results.append({"case": index, "similarity": score, "latency_ms": latency_ms, "passed": passed})
        mean_latency = round(sum(latencies) / len(latencies), 3) if latencies else 0.0
        return {
            "success": all(result["passed"] for result in results),
            "benchmark": "embedding_benchmark",
            "summary": {
                "case_count": len(results),
                "mean_latency_ms": mean_latency,
                "latency_threshold_ms": BENCHMARK_THRESHOLDS["maximum_embedding_latency_ms"],
            },
            "results": results,
        }


embedding_benchmark = EmbeddingBenchmark()
