"""Normalization helpers for AIRA rule score inputs."""

from __future__ import annotations


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Clamp a numeric value into an inclusive range."""
    return max(minimum, min(maximum, value))


def normalize_cgpa(cgpa: float, scale: float = 10.0) -> float:
    """Normalize a CGPA value to a 0-100 scale."""
    if scale <= 0:
        raise ValueError("CGPA scale must be greater than zero.")
    return round(clamp((cgpa / scale) * 100.0), 2)


def normalize_count(count: int, target_count: int) -> float:
    """Normalize an activity count to a 0-100 completion score."""
    if target_count <= 0:
        raise ValueError("Target count must be greater than zero.")
    return round(clamp((max(count, 0) / target_count) * 100.0), 2)


def normalize_skills(candidate_skills: list[str], required_skills: list[str] | None = None) -> float:
    """Normalize skills by either required-skill coverage or portfolio breadth."""
    unique_candidate_skills = {skill.strip().lower() for skill in candidate_skills if skill.strip()}
    if required_skills:
        unique_required_skills = {skill.strip().lower() for skill in required_skills if skill.strip()}
        if not unique_required_skills:
            return 0.0
        matched = unique_candidate_skills.intersection(unique_required_skills)
        return round(clamp((len(matched) / len(unique_required_skills)) * 100.0), 2)
    return normalize_count(len(unique_candidate_skills), target_count=10)


def normalize_internships(count: int) -> float:
    """Normalize internships with two internships considered full credit."""
    return normalize_count(count, target_count=2)


def normalize_hackathons(count: int) -> float:
    """Normalize hackathons with three hackathons considered full credit."""
    return normalize_count(count, target_count=3)
