from app.utils.validators import Validator

from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_hackathons,
    normalize_internships
)

from app.services.aira.rule_engine import (
    calculate_rule_score
)

from app.services.aira.score_explainer import (
    explain_score
)


def run_aira_engine(profile):

    Validator.validate_cgpa(profile["cgpa"])

    profile["cgpa"] = normalize_cgpa(profile["cgpa"])

    profile["hackathons"] = normalize_hackathons(
        profile["hackathons"]
    )

    profile["internships"] = normalize_internships(
        profile["internships"]
    )

    score = calculate_rule_score(profile)

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

        "cgpa": 8.7,

        "skills": [
            "Python",
            "FastAPI",
            "React",
            "SQL"
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

    print("\n========== FINAL AIRA RESULT ==========")

    print("\nAIRA SCORE:")
    print(result["aira_score"])

    print("\nEXPLANATION:")

    for line in result["explanation"]:
        print("•", line)
        