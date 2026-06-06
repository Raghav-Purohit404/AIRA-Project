"""Deterministic non-LLM AIRA rule scoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_count,
    normalize_hackathons,
    normalize_internships,
    normalize_skills,
)
from app.services.aira.weight_config import DEFAULT_WEIGHTS, ScoreWeights


@dataclass(frozen=True)
class CandidateProfile:
    """Candidate attributes needed for rule-based scoring."""

    cgpa: float
    skills: list[str] = field(default_factory=list)
    projects: int = 0
    internships: int = 0
    hackathons: int = 0
    achievements: int = 0


@dataclass(frozen=True)
class RuleScoreResult:
    """Detailed rule score output."""

    total_score: float
    components: dict[str, float]
    normalized_inputs: dict[str, float]


class RuleEngine:
    """Calculate rule-based candidate scores from normalized inputs."""

    def __init__(self, weights: ScoreWeights = DEFAULT_WEIGHTS) -> None:
        self.weights = weights

    def score(self, profile: CandidateProfile, required_skills: list[str] | None = None) -> RuleScoreResult:
        """Return the weighted rule score for a candidate profile."""
        normalized = {
            "cgpa": normalize_cgpa(profile.cgpa),
            "skills": normalize_skills(profile.skills, required_skills),
            "projects": normalize_count(profile.projects, target_count=4),
            "internships": normalize_internships(profile.internships),
            "hackathons": normalize_hackathons(profile.hackathons),
            "achievements": normalize_count(profile.achievements, target_count=5),
        }
        components = {
            name: round((value / 100.0) * getattr(self.weights, name), 2)
            for name, value in normalized.items()
        }
        return RuleScoreResult(
            total_score=round(sum(components.values()), 2),
            components=components,
            normalized_inputs=normalized,
        )


def calculate_rule_score(
    profile: CandidateProfile | dict[str, object],
    required_skills: list[str] | None = None,
) -> dict[str, object]:
    """Convenience wrapper returning a structured JSON-serializable score."""
    if isinstance(profile, dict):
        projects = profile.get("projects", 0)
        internships = profile.get("internships", 0)
        hackathons = profile.get("hackathons", 0)
        achievements = profile.get("achievements", 0)
        profile = CandidateProfile(
            cgpa=float(profile.get("cgpa", 0.0)),
            skills=[str(skill) for skill in profile.get("skills", [])],
            projects=len(projects) if isinstance(projects, list) else int(projects),
            internships=len(internships) if isinstance(internships, list) else int(internships),
            hackathons=len(hackathons) if isinstance(hackathons, list) else int(hackathons),
            achievements=len(achievements) if isinstance(achievements, list) else int(achievements),
        )
    result = RuleEngine().score(profile, required_skills)
    return {
        "success": True,
        "total_score": result.total_score,
        "components": result.components,
        "normalized_inputs": result.normalized_inputs,
    }
