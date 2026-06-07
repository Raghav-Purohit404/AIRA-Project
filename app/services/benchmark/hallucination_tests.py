"""Grounding checks for LLM-generated text."""

from __future__ import annotations

from typing import Any

from app.services.llm_local.hallucination_guard import HallucinationGuard


class HallucinationBenchmark:
    """Evaluate whether generated claims are supported by source context."""

    def __init__(self, guard: HallucinationGuard | None = None) -> None:
        self.guard = guard or HallucinationGuard()

    def run(self, cases: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Run grounding checks and return structured results."""
        samples = cases or [
            {
                "context": "The student knows Python, SQL, and FastAPI.",
                "output": "The student knows Python and FastAPI.",
            }
        ]
        results = [self.guard.validate(str(case["output"]), str(case["context"])) for case in samples]
        return {
            "success": all(result.supported for result in results),
            "benchmark": "hallucination_tests",
            "summary": {"case_count": len(results), "supported": sum(result.supported for result in results)},
            "results": [result.model_dump() for result in results],
        }


hallucination_benchmark = HallucinationBenchmark()
