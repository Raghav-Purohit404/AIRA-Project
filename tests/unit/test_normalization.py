<<<<<<< HEAD
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
=======
from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_hackathons,
    normalize_internships
)


def test_normalization():

    print("\n========== CGPA NORMALIZATION ==========")

    print("8.756  ->", normalize_cgpa(8.756))
    print("15     ->", normalize_cgpa(15))
    print("-2     ->", normalize_cgpa(-2))

    print("\n========== HACKATHON NORMALIZATION ==========")

    print("5      ->", normalize_hackathons(5))
    print("20     ->", normalize_hackathons(20))

    print("\n========== INTERNSHIP NORMALIZATION ==========")

    print("2      ->", normalize_internships(2))
    print("10     ->", normalize_internships(10))

    assert normalize_cgpa(15) == 10
    assert normalize_hackathons(20) == 10
    assert normalize_internships(10) == 5
>>>>>>> 6f50f52c80d4b77411b7a82311c9bf3403b4fd7e
