"""Tests for AIRA normalization helpers."""

from app.services.aira.normalization import normalize_cgpa, normalize_hackathons, normalize_internships, normalize_skills
import pytest


def test_normalize_cgpa_to_100_scale() -> None:
    """CGPA should be converted to a clamped 0-100 scale."""
    assert normalize_cgpa(8.5) == 85.0
    assert normalize_cgpa(11.0) == 100.0


def test_normalize_activity_weighting() -> None:
    """Internships and hackathons should use their configured full-credit targets."""
    assert normalize_internships(1) == 50.0
    assert normalize_hackathons(2) == 66.67


def test_normalize_skills_against_required_skills() -> None:
    """Required skills should be scored by coverage."""
    assert normalize_skills(["Python", "React"], ["python", "sql"]) == 50.0


def test_normalize_cgpa_rejects_invalid_scale() -> None:
    """CGPA normalization should reject impossible scales."""
    with pytest.raises(ValueError):
        normalize_cgpa(8.0, scale=0)
