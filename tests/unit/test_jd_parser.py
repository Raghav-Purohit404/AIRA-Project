"""Tests for rule-based JD parsing."""

from app.services.jd.jd_parser import parse_jd
from app.services.jd.jd_validator import validate_jd_text


def test_parse_jd_extracts_required_fields() -> None:
    """JD parser should extract skills, technologies, experience, and education."""
    result = parse_jd("Need Python, FastAPI and PostgreSQL. 2 years experience. Bachelor degree preferred.")

    assert result["success"] is True
    assert "Python" in result["skills"]
    assert "FastAPI" in result["technologies"]
    assert result["experience_requirements"]
    assert result["education_requirements"]


def test_validate_jd_text_rejects_short_text() -> None:
    """JD validation should reject underspecified text."""
    assert validate_jd_text("Python")["is_valid"] is False


def test_parse_jd_handles_missing_optional_sections() -> None:
    """JD parser should return empty lists for absent categories."""
    result = parse_jd("We are hiring a thoughtful teammate for product support and documentation.")

    assert result["skills"] == []
    assert result["technologies"] == []
    assert result["experience_requirements"] == []
