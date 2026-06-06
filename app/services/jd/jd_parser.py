"""Rule-based job description parser."""

from __future__ import annotations

import re


KNOWN_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "fastapi",
    "django",
    "sql",
    "postgresql",
    "machine learning",
    "data analysis",
    "docker",
    "aws",
    "azure",
}

TECHNOLOGY_ALIASES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "fastapi": "FastAPI",
    "react": "React",
    "docker": "Docker",
    "aws": "AWS",
    "azure": "Azure",
}


def _find_known_terms(text: str, terms: set[str]) -> list[str]:
    """Find known terms in free-form text."""
    lowered = text.lower()
    matches = []
    for term in terms:
        if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", lowered):
            matches.append(term.title() if term != "sql" else "SQL")
    return sorted(set(matches))


def parse_jd(text: str) -> dict[str, object]:
    """Extract skills, technologies, experience, and education from a JD."""
    cleaned_text = " ".join(text.split())
    lowered = cleaned_text.lower()
    skills = _find_known_terms(cleaned_text, KNOWN_SKILLS)
    technologies = sorted(
        {
            display
            for alias, display in TECHNOLOGY_ALIASES.items()
            if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", lowered)
        }
    )
    experience_matches = re.findall(
        r"(\d+\+?\s*(?:-\s*\d+\s*)?(?:years?|yrs?)(?:\s+of)?\s+experience)",
        cleaned_text,
        flags=re.IGNORECASE,
    )
    education_matches = re.findall(
        r"((?:bachelor|master|b\.?tech|m\.?tech|degree|graduate)[^.;,\n]*)",
        cleaned_text,
        flags=re.IGNORECASE,
    )
    return {
        "success": True,
        "skills": skills,
        "technologies": technologies,
        "experience_requirements": sorted(set(match.strip() for match in experience_matches)),
        "education_requirements": sorted(set(match.strip() for match in education_matches)),
    }
