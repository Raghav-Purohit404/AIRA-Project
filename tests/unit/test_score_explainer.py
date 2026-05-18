from app.services.aira.score_explainer import (
    explain_score
)

from app.services.aira.rule_engine import (
    calculate_rule_score
)


def test_score_explainer():

    profile = {
        "cgpa": 8.7,
        "skills": [
            "Python",
            "FastAPI",
            "React",
            "SQL",
            "Docker"
        ],
        "projects": [
            "AIRA",
            "Resume Analyzer",
            "Chatbot"
        ],
        "internships": 2,
        "hackathons": 3
    }

    score = calculate_rule_score(profile)

    explanation = explain_score(
        profile,
        score
    )

    print("\n========== FINAL AIRA SCORE ==========")
    print(score)

    print("\n========== SCORE EXPLANATION ==========")

    for line in explanation:
        print("•", line)

    assert isinstance(explanation, list)