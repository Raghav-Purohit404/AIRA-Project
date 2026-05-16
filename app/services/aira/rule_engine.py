from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_hackathons,
    normalize_internships
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
    score += cgpa * 3

    # SKILL SCORE
    score += min(len(skills) * 2, 25)

    # PROJECT SCORE
    score += min(len(projects) * 3, 20)

    # INTERNSHIP SCORE
    score += internships * 3

    # HACKATHON SCORE
    score += hackathons * 1

    return round(score, 2)
