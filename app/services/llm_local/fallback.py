"""Recovery and deterministic fallback helpers for local LLM output."""

from __future__ import annotations

import json
import re
from typing import Any


def recover_json(text: str) -> dict[str, Any] | list[Any] | None:
    """Recover the first valid JSON object or array from model output."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    for candidate in (cleaned, *_balanced_json_candidates(cleaned)):
        try:
            value = json.loads(candidate)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(value, (dict, list)):
            return value
    return None


def regex_skill_extraction(text: str) -> dict[str, list[str]]:
    """Extract known technology terms when the LLM is unavailable."""
    catalog = {
        "programming_languages": ["Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "SQL"],
        "frameworks": ["FastAPI", "Django", "Flask", "React", "Angular", "Vue", "Spring", "Node.js"],
        "tools": ["Git", "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Redis", "Linux"],
        "cloud_technologies": ["AWS", "Azure", "GCP", "Google Cloud"],
    }
    extracted: dict[str, list[str]] = {}
    for category, terms in catalog.items():
        extracted[category] = [
            term for term in terms if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, re.IGNORECASE)
        ]
    extracted["technical_skills"] = list(
        dict.fromkeys(term for values in extracted.values() for term in values)
    )
    return extracted


def timeout_fallback(operation: str, source_text: str = "") -> dict[str, Any]:
    """Return a structured fallback result after a timeout."""
    result: dict[str, Any] = {"success": True, "fallback": True, "reason": "timeout", "operation": operation}
    if operation == "skill_extraction":
        result["data"] = regex_skill_extraction(source_text)
    return result


def _balanced_json_candidates(text: str) -> list[str]:
    """Extract balanced object and array substrings."""
    candidates: list[str] = []
    starts = sorted(
        (index, opening, closing)
        for opening, closing in (("{", "}"), ("[", "]"))
        for index in [text.find(opening)]
        if index >= 0
    )
    for start, opening, closing in starts:
        depth = 0
        quoted = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                quoted = not quoted
            if quoted:
                continue
            if char == opening:
                depth += 1
            elif char == closing:
                depth -= 1
                if depth == 0:
                    candidates.append(text[start : index + 1])
                    break
    return candidates
