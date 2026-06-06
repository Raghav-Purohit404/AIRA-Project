"""Reusable validation helpers for AIRA services and routes."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SKILL_PATTERN = re.compile(r"^[A-Za-z0-9+#.\- ]{2,64}$")
REQUIRED_RESUME_FIELDS = {"name", "email", "skills", "projects"}


def is_valid_email(email: str) -> bool:
    """Return whether text resembles an email address."""
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def validate_email(email: str) -> str:
    """Validate and normalize an email address."""
    normalized_email = email.strip().lower()
    if not is_valid_email(normalized_email):
        raise ValueError("Invalid email address.")
    return normalized_email


def validate_cgpa(cgpa: float, scale: float = 10.0) -> float:
    """Validate CGPA against a configurable positive scale."""
    if scale <= 0:
        raise ValueError("CGPA scale must be greater than zero.")
    if cgpa < 0 or cgpa > scale:
        raise ValueError(f"CGPA must be between 0 and {scale}.")
    return cgpa


def validate_skill(skill: str) -> str:
    """Validate and normalize one skill label."""
    normalized_skill = " ".join(skill.strip().split())
    if not SKILL_PATTERN.fullmatch(normalized_skill):
        raise ValueError("Skill must be 2-64 characters and contain only safe label characters.")
    return normalized_skill


def validate_skills(skills: Iterable[str], allow_empty: bool = False) -> list[str]:
    """Validate a skill collection and remove case-insensitive duplicates."""
    seen: set[str] = set()
    normalized_skills: list[str] = []
    for skill in skills:
        normalized_skill = validate_skill(skill)
        key = normalized_skill.lower()
        if key not in seen:
            seen.add(key)
            normalized_skills.append(normalized_skill)

    if not allow_empty and not normalized_skills:
        raise ValueError("At least one skill is required.")
    return normalized_skills


def validate_resume_fields(resume: dict[str, Any]) -> dict[str, Any]:
    """Validate required structured resume fields."""
    missing = sorted(field for field in REQUIRED_RESUME_FIELDS if field not in resume)
    if missing:
        raise ValueError(f"Missing resume fields: {', '.join(missing)}.")
    validate_email(str(resume["email"]))
    validate_skills(resume.get("skills", []))
    return resume


def require_non_empty(value: str, field_name: str) -> None:
    """Raise a ValueError when a required string is empty."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty.")


def require_keys(payload: dict[str, Any], required_keys: Iterable[str]) -> None:
    """Raise a ValueError when required dictionary keys are missing."""
    missing = sorted(key for key in required_keys if key not in payload)
    if missing:
        raise ValueError(f"Missing required keys: {', '.join(missing)}.")
