# placeholder
def track_recruiter_signals(student):

    strong_signals = []

    high_value_skills = [
        "Python",
        "FastAPI",
        "Docker",
        "React",
        "AWS",
        "Machine Learning"
    ]

    for skill in student["skills"]:

        if skill in high_value_skills:
            strong_signals.append(skill)

    if student["internships"] > 0:
        strong_signals.append(
            "Industry Experience"
        )

    if student["projects"] >= 3:
        strong_signals.append(
            "Strong Project Portfolio"
        )

    if student["cgpa"] >= 8.5:
        strong_signals.append(
            "High Academic Performance"
        )

    return {
        "strong_signals": strong_signals
    }


if __name__ == "__main__":

    sample_student = {
        "cgpa": 8.7,
        "projects": 4,
        "internships": 1,
        "skills": [
            "Python",
            "FastAPI",
            "Docker"
        ]
    }

    result = track_recruiter_signals(sample_student)

    print(result)
