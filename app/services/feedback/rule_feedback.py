# placeholder
def generate_rule_feedback(student):

    suggestions = []

    if student["cgpa"] < 7.5:
        suggestions.append(
            "Focus on improving academic consistency."
        )

    if student["projects"] < 2:
        suggestions.append(
            "Build more hands-on technical projects."
        )

    if student["internships"] == 0:
        suggestions.append(
            "Apply for internships to gain industry experience."
        )

    if student["hackathons"] == 0:
        suggestions.append(
            "Participate in hackathons to improve problem-solving skills."
        )

    if len(student["skills"]) < 3:
        suggestions.append(
            "Expand your technical skill set."
        )

    return {
        "suggestions": suggestions
    }


if __name__ == "__main__":

    sample_student = {
        "cgpa": 7.1,
        "projects": 1,
        "internships": 0,
        "hackathons": 0,
        "skills": ["Java"]
    }

    result = generate_rule_feedback(sample_student)

    print(result)
