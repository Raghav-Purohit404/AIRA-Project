from app.services.aira.rule_engine import (
    calculate_rule_score
)


def test_rule_score():

    profile = {
        "cgpa": 8.5,
        "skills": [
            "Python",
            "FastAPI",
            "React"
        ],
        "projects": [
            "Chatbot",
            "Dashboard"
        ],
        "internships": 1,
        "hackathons": 2
    }

    score = calculate_rule_score(profile)

    print("\n========== RULE ENGINE OUTPUT ==========")
    print("FINAL AIRA SCORE:", score)

    assert score > 0