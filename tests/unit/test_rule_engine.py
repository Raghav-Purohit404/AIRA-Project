"""Tests for deterministic AIRA rule scoring."""

from app.services.aira.rule_engine import CandidateProfile, RuleEngine, calculate_rule_score


def test_rule_engine_returns_component_breakdown() -> None:
    """The rule engine should return total score and component details."""
    profile = CandidateProfile(
        cgpa=9.0,
        skills=["Python", "FastAPI", "React"],
        projects=4,
        internships=2,
        hackathons=3,
        achievements=5,
    )

    result = RuleEngine().score(profile, required_skills=["python", "fastapi", "sql"])

    assert result.total_score > 80
    assert set(result.components) == {"cgpa", "skills", "projects", "internships", "hackathons", "achievements"}


def test_calculate_rule_score_is_json_serializable() -> None:
    """The convenience wrapper should return structured JSON data."""
    result = calculate_rule_score(CandidateProfile(cgpa=8.0, skills=["Python"]))

    assert result["success"] is True
    assert "total_score" in result


def test_rule_engine_clamps_extreme_profile_values() -> None:
    """Extreme counts should not exceed configured component weights."""
    profile = CandidateProfile(
        cgpa=12.0,
        skills=[f"Skill {index}" for index in range(10)],
        projects=20,
        internships=20,
        hackathons=20,
        achievements=20,
    )

    result = RuleEngine().score(profile)

    assert result.total_score == 100.0
