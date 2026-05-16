from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_hackathons,
    normalize_internships
)

from app.services.aira.weight_config import (
    MAX_CGPA_SCORE,
    MAX_SKILL_SCORE,
    MAX_PROJECT_SCORE,
    MAX_INTERNSHIP_SCORE,
    MAX_HACKATHON_SCORE
)


def calculate_rule_score(profile: dict):

    score = 0

    cgpa = normalize_cgpa(
        profile.get("cgpa", 0)
    )

    internships = normalize_internships(
        profile.get("internships", 0)
    )

    hackathons = normalize_hackathons(
        profile.get("hackathons", 0)
    )

    skills = profile.get("skills", [])
    projects = profile.get("projects", [])

    # CGPA SCORE
    cgpa_score = (
        (cgpa / 10) * MAX_CGPA_SCORE
    )

    # SKILLS SCORE
    skill_score = min(
        len(skills) * 4,
        MAX_SKILL_SCORE
    )

    # PROJECT SCORE
    project_score = min(
        len(projects) * 4,
        MAX_PROJECT_SCORE
    )

    # INTERNSHIP SCORE
    internship_score = min(
        internships * 5,
        MAX_INTERNSHIP_SCORE
    )

    # HACKATHON SCORE
    hackathon_score = min(
        hackathons * 4,
        MAX_HACKATHON_SCORE
    )

    score = (
        cgpa_score
        + skill_score
        + project_score
        + internship_score
        + hackathon_score
    )

    return round(score, 2)