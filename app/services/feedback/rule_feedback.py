"""Rules for deterministic candidate feedback generation."""

from __future__ import annotations

from typing import Any

from app.services.jd.jd_skill_mapper import jd_skill_mapper


def generate_rule_feedback(profile: dict[str, Any]) -> dict[str, list[str]]:
    """Generate strengths, weaknesses, and recommendations from profile fields."""
    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendations: list[str] = []

    cgpa = float(profile.get("cgpa", 0) or 0)
    internships = int(profile.get("internships", 0) or 0)
    projects = int(profile.get("projects", 0) or 0)
    skills = [skill for skill in profile.get("skills", []) if str(skill).strip()]

    if cgpa >= 8.5:
        strengths.append("Strong CGPA")
    elif cgpa < 7.0:
        weaknesses.append("CGPA below target range")
        recommendations.append("Improve academic consistency and highlight stronger coursework")

    if internships > 0:
        strengths.append("Has internship experience")
    else:
        weaknesses.append("No internships")
        recommendations.append("Complete one internship")

    if projects >= 3:
        strengths.append("Strong project portfolio")
    else:
        weaknesses.append("Limited project portfolio")
        recommendations.append("Build at least three role-relevant projects")

    if len(set(map(str.lower, skills))) >= 5:
        strengths.append("Broad skill set")
    else:
        weaknesses.append("Limited skills coverage")
        recommendations.append("Add role-relevant technical skills")

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
    }


def generate_profile_feedback(profile: dict[str, Any], target_skills: list[str] | None = None) -> dict[str, list[str]]:
    """Generate feedback from a serialized StudentProfile-like dictionary."""
    academic = profile.get("academic", {})
    skill_items = profile.get("skills", [])
    project_items = profile.get("projects", [])
    internship_items = profile.get("internships", [])
    hackathon_items = profile.get("hackathons", [])
    achievement_items = profile.get("achievements", [])
    skill_names = jd_skill_mapper.normalize_skills([str(item.get("name", item)) if isinstance(item, dict) else str(item) for item in skill_items])
    feedback = generate_rule_feedback(
        {
            "cgpa": academic.get("cgpa", 0),
            "skills": skill_names,
            "projects": len(project_items),
            "internships": len(internship_items),
            "hackathons": len(hackathon_items),
            "achievements": len(achievement_items),
        }
    )

    targets = {skill.casefold() for skill in jd_skill_mapper.normalize_skills(target_skills or [])}
    existing = {skill.strip().lower() for skill in skill_names if skill.strip()}
    missing_skills = sorted(targets - existing)
    if missing_skills:
        feedback["weaknesses"].append("Skill gaps for target role")
        feedback["recommendations"].append(f"Add or demonstrate these skills: {', '.join(missing_skills)}")
    if not hackathon_items:
        feedback["recommendations"].append("Participate in one hackathon to demonstrate applied problem solving")
    if not achievement_items:
        feedback["recommendations"].append("Document certifications, awards, or measurable achievements")
    return feedback
