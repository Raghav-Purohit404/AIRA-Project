"""ATS-aware semantic weighting for extracted skills."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class SkillScore:
    """Weighted semantic signal for one skill."""

    skill: str
    confidence: float
    ats_weight: float
    semantic_relevance: float
    weighted_score: float

    def to_dict(self) -> dict[str, str | float]:
        """Return a JSON-serializable score."""
        return {
            "skill": self.skill,
            "confidence": self.confidence,
            "ats_weight": self.ats_weight,
            "semantic_relevance": self.semantic_relevance,
            "weighted_score": self.weighted_score,
        }


class LLMScorer:
    """Combine extraction confidence, ATS importance, and relevance."""

    def score_skill(
        self,
        skill: str,
        confidence: float,
        required_skills: Iterable[str] = (),
        semantic_relevance: float = 0.0,
    ) -> SkillScore:
        """Calculate a bounded weighted score for one skill."""
        required = {item.casefold() for item in required_skills}
        bounded_confidence = max(0.0, min(1.0, confidence))
        bounded_relevance = max(0.0, min(1.0, semantic_relevance))
        ats_weight = 1.2 if skill.casefold() in required else 1.0
        relevance_boost = 1.0 + (0.2 * bounded_relevance)
        weighted = min(1.5, bounded_confidence * ats_weight * relevance_boost)
        return SkillScore(
            skill=skill,
            confidence=round(bounded_confidence, 4),
            ats_weight=ats_weight,
            semantic_relevance=round(bounded_relevance, 4),
            weighted_score=round(weighted, 4),
        )

    def score_many(
        self,
        skills: Iterable[tuple[str, float]],
        required_skills: Iterable[str] = (),
        relevance_by_skill: dict[str, float] | None = None,
    ) -> list[dict[str, str | float]]:
        """Score and sort multiple skills for downstream AIRA weighting."""
        relevance = relevance_by_skill or {}
        scores = [
            self.score_skill(skill, confidence, required_skills, relevance.get(skill, 0.0))
            for skill, confidence in skills
        ]
        return [score.to_dict() for score in sorted(scores, key=lambda item: -item.weighted_score)]

    def prepare_lora_training_record(self, score: SkillScore, label: float) -> dict[str, object]:
        """Build a future LoRA-compatible supervised record."""
        return {"input": score.to_dict(), "target": max(0.0, min(1.0, label))}


llm_scorer = LLMScorer()
