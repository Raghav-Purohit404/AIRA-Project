"""End-to-end local LLM pipeline with deterministic degradation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.llm_local.fallback import regex_skill_extraction
from app.services.llm_local.hallucination_guard import GroundingResult, HallucinationGuard
from app.services.llm_local.llm_preprocessor import LLMPreprocessor
from app.services.llm_local.llm_scorer import LLMScorer
from app.services.llm_local.llm_service import LLMServiceError, OllamaLLMService
from app.services.llm_local.prompt_manager import prompt_manager


SKILL_GROUPS = (
    "technical_skills",
    "frameworks",
    "tools",
    "programming_languages",
    "cloud_technologies",
)


@dataclass(frozen=True)
class LLMPipelineResult:
    """Serializable result for one local LLM pipeline execution."""

    success: bool
    mode: str
    skills: dict[str, list[str]]
    scored_skills: list[dict[str, str | float]]
    grounding: GroundingResult
    response: str | dict[str, Any] | list[Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "success": self.success,
            "mode": self.mode,
            "skills": self.skills,
            "scored_skills": self.scored_skills,
            "grounding": self.grounding.model_dump(),
            "response": self.response,
            "error": self.error,
        }


class LocalLLMPipeline:
    """Coordinate prompt preparation, generation, fallback, scoring, and grounding."""

    def __init__(
        self,
        service: OllamaLLMService | None = None,
        preprocessor: LLMPreprocessor | None = None,
        scorer: LLMScorer | None = None,
        guard: HallucinationGuard | None = None,
    ) -> None:
        self.service = service or OllamaLLMService()
        self.preprocessor = preprocessor or LLMPreprocessor()
        self.scorer = scorer or LLMScorer()
        self.guard = guard or HallucinationGuard()

    def run_skill_pipeline(
        self,
        text: str,
        required_skills: list[str] | None = None,
    ) -> LLMPipelineResult:
        """Run the LLM-assisted skill pipeline with deterministic fallback."""
        required = required_skills or []
        cleaned = self.preprocessor.clean(text)
        prompt = prompt_manager.render("skill_extraction", text=cleaned)
        mode = "live_ollama"
        response: str | dict[str, Any] | list[Any] | None = None
        error: str | None = None

        try:
            response = self.service.generate(prompt, structured=True)
            if not isinstance(response, dict):
                raise LLMServiceError("Structured skill extraction returned a non-object payload.")
            skills = self._normalize_skill_groups(response)
        except LLMServiceError as exc:
            mode = "deterministic_fallback"
            error = str(exc)
            skills = regex_skill_extraction(cleaned)

        skills = self._merge_skill_groups(regex_skill_extraction(cleaned), skills)
        skills = self._filter_supported_skills(skills, cleaned)
        flat_skills = list(dict.fromkeys(skill for values in skills.values() for skill in values))
        scored = self.scorer.score_many(
            [(skill, 1.0 if skill in required else 0.8) for skill in flat_skills],
            required_skills=required,
        )
        grounded_text = ", ".join(flat_skills)
        grounding = self.guard.validate(grounded_text, cleaned)
        return LLMPipelineResult(
            success=bool(flat_skills) and grounding.supported,
            mode=mode,
            skills=skills,
            scored_skills=scored,
            grounding=grounding,
            response=response,
            error=error,
        )

    def _merge_skill_groups(
        self,
        baseline: dict[str, list[str]],
        generated: dict[str, list[str]],
    ) -> dict[str, list[str]]:
        """Merge deterministic extraction with model extraction without duplicates."""
        return {
            category: list(
                dict.fromkeys(
                    [
                        *baseline.get(category, []),
                        *generated.get(category, []),
                    ]
                )
            )
            for category in SKILL_GROUPS
        }

    def _filter_supported_skills(
        self,
        skills: dict[str, list[str]],
        source_text: str,
    ) -> dict[str, list[str]]:
        """Drop generated skill terms that are not lexically grounded in the source."""
        return {
            category: [
                skill
                for skill in values
                if self.guard.validate(skill, source_text).supported
            ]
            for category, values in skills.items()
        }

    def _normalize_skill_groups(self, payload: dict[str, Any]) -> dict[str, list[str]]:
        """Normalize model JSON into the project skill-group schema."""
        normalized: dict[str, list[str]] = {}
        for category in SKILL_GROUPS:
            values = payload.get(category, [])
            normalized[category] = (
                list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))
                if isinstance(values, list)
                else []
            )
        normalized["technical_skills"] = list(
            dict.fromkeys(
                [
                    *normalized.get("technical_skills", []),
                    *normalized.get("programming_languages", []),
                    *normalized.get("frameworks", []),
                    *normalized.get("tools", []),
                    *normalized.get("cloud_technologies", []),
                ]
            )
        )
        return normalized
