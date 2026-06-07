"""AIRA scoring reliability benchmarks."""

from __future__ import annotations

from typing import Any

from app.models.student_profile import StudentProfile
from app.services.aira.aira_engine import AIRAEngine


class ScoringBenchmark:
    """Evaluate deterministic score ranges and reliability."""

    def __init__(self, engine: AIRAEngine | None = None) -> None:
        self.engine = engine or AIRAEngine()

    def run(self, profiles: list[StudentProfile | dict[str, Any]] | None = None) -> dict[str, Any]:
        """Score profiles and verify bounded outputs."""
        samples = profiles or []
        results: list[dict[str, Any]] = []
        for index, profile_input in enumerate(samples, start=1):
            profile = profile_input if isinstance(profile_input, StudentProfile) else StudentProfile.model_validate(profile_input)
            score = self.engine.score_profile(profile)
            final_score = score.breakdown.final_score
            results.append(
                {
                    "case": index,
                    "student_id": profile.id,
                    "score": final_score,
                    "readiness_level": score.readiness_level,
                    "passed": 0.0 <= final_score <= 100.0,
                }
            )
        return {
            "success": all(result["passed"] for result in results),
            "benchmark": "scoring_benchmark",
            "summary": {"profile_count": len(results)},
            "results": results,
        }


scoring_benchmark = ScoringBenchmark()
