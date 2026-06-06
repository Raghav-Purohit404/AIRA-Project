"""Structured skill extraction using Ollama with deterministic fallback."""

from __future__ import annotations

from typing import Any

from app.services.llm_local.fallback import regex_skill_extraction
from app.services.llm_local.llm_service import LLMServiceError, OllamaLLMService, llm_service
from app.services.llm_local.prompt_manager import prompt_manager


def extract_skill_groups(
    text: str,
    service: OllamaLLMService = llm_service,
) -> dict[str, list[str]]:
    """Extract categorized skills as structured JSON."""
    if not text.strip():
        return regex_skill_extraction("")
    try:
        result = service.generate(
            prompt_manager.render("skill_extraction", text=text),
            structured=True,
        )
    except LLMServiceError:
        return regex_skill_extraction(text)
    if not isinstance(result, dict):
        return regex_skill_extraction(text)
    normalized: dict[str, list[str]] = {}
    for category in (
        "technical_skills",
        "frameworks",
        "tools",
        "programming_languages",
        "cloud_technologies",
    ):
        values: Any = result.get(category, [])
        normalized[category] = (
            list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))
            if isinstance(values, list)
            else []
        )
    return normalized


def extract_skills(text: str) -> list[str]:
    """Return a flattened skill list for existing callers."""
    groups = extract_skill_groups(text)
    return list(dict.fromkeys(skill for values in groups.values() for skill in values))
