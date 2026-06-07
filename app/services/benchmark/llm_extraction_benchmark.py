"""Benchmarks for deterministic and LLM-assisted extraction."""

from __future__ import annotations

from typing import Any

from app.services.benchmark.evaluation_metrics import recall_score
from app.services.llm_local.skill_extractor import extract_skills


class LLMExtractionBenchmark:
    """Evaluate skill extraction accuracy."""

    def run(self, cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Run extraction cases and return recall-oriented scores."""
        samples = cases or [{"text": "Python, SQL, FastAPI and Docker", "expected": ["Python", "SQL", "FastAPI"]}]
        results: list[dict[str, Any]] = []
        for index, case in enumerate(samples, start=1):
            actual = extract_skills(str(case["text"]))
            expected = [str(item) for item in case.get("expected", [])]
            recall = recall_score(expected, actual)
            results.append({"case": index, "expected": expected, "actual": actual, "recall": recall, "passed": recall >= 0.7})
        return {
            "success": all(result["passed"] for result in results),
            "benchmark": "llm_extraction_benchmark",
            "summary": {"case_count": len(results)},
            "results": results,
        }


llm_extraction_benchmark = LLMExtractionBenchmark()
