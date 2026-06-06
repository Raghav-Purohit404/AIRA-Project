"""Validation helpers for job description content."""

from __future__ import annotations


def validate_jd_text(text: str) -> dict[str, object]:
    """Validate a job description before parsing."""
    errors: list[str] = []
    if not text or not text.strip():
        errors.append("Job description text is required.")
    if len(text.strip()) < 30:
        errors.append("Job description must contain at least 30 characters.")
    return {"is_valid": not errors, "errors": errors}
