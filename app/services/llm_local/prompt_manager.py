"""Reusable prompt templates for local LLM operations."""

from __future__ import annotations

from string import Template


PROMPTS: dict[str, Template] = {
    "skill_extraction": Template(
        "Extract technical skills from the text. Return JSON with arrays named "
        "technical_skills, frameworks, tools, programming_languages, and cloud_technologies.\nText:\n$text"
    ),
    "achievement_classification": Template(
        "Classify each achievement by category and impact. Return strict JSON.\nAchievements:\n$text"
    ),
    "ats_enhancement": Template(
        "Improve this resume content for ATS matching without inventing facts. Return strict JSON.\n$text"
    ),
    "semantic_scoring": Template(
        "Score candidate relevance to the job from 0 to 100 with confidence and reasons. "
        "Return strict JSON.\nCandidate:\n$profile\nJob:\n$job"
    ),
    "feedback_generation": Template(
        "Generate concise evidence-based strengths, gaps, and actions as strict JSON.\nProfile:\n$profile"
    ),
}


class PromptManager:
    """Render registered prompts with validated variables."""

    def render(self, name: str, **values: object) -> str:
        """Render a named template."""
        template = PROMPTS.get(name)
        if template is None:
            raise KeyError(f"Unknown prompt template: {name}")
        return template.substitute({key: str(value) for key, value in values.items()})

    def names(self) -> tuple[str, ...]:
        """Return available prompt identifiers."""
        return tuple(PROMPTS)


prompt_manager = PromptManager()
