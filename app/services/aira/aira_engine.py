from app.utils.validators import (
    validate_cgpa,
    validate_internships,
    validate_hackathons
)

from app.services.aira.rule_engine import (
    calculate_rule_score
)

from app.services.aira.score_explainer import (
    explain_score
)


def run_aira_engine(profile: dict):

    # VALIDATION
    validate_cgpa(
        profile.get("cgpa", 0)
    )

    validate_internships(
        profile.get("internships", 0)
    )

    validate_hackathons(
        profile.get("hackathons", 0)
    )

    # SCORE CALCULATION
    score = calculate_rule_score(
        profile
    )

    # SCORE EXPLANATION
    explanation = explain_score(
        profile,
        score
    )

    return {
        "aira_score": score,
        "explanation": explanation
    }


if __name__ == "__main__":

    sample_profile = {
        "cgpa": 8.8,

        "skills": [
            "Python",
            "FastAPI",
            "React",
            "Docker"
        ],

        "projects": [
            "AIRA",
            "Resume Analyzer"
        ],

        "internships": 2,

        "hackathons": 3
    }

    result = run_aira_engine(
        sample_profile
    )

    print("\n========== AIRA RESULT ==========\n")

    print(
        f"AIRA SCORE : {result['aira_score']}\n"
    )

    print("EXPLANATION:\n")

    for item in result["explanation"]:
        print(f"• {item}")

    print("\n================================\n")