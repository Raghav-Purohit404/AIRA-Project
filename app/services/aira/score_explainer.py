def explain_score(profile: dict, score: float | dict[str, object]):
    if isinstance(score, dict):
        score = float(score.get("total_score", 0.0))

    explanation = []

    cgpa = profile.get("cgpa", 0)
    skills = profile.get("skills", [])
    projects = profile.get("projects", [])
    internships = profile.get("internships", 0)
    hackathons = profile.get("hackathons", 0)

    # CGPA ANALYSIS
    if cgpa >= 8.5:
        explanation.append(
            "Strong academic performance"
        )

    elif cgpa >= 7:
        explanation.append(
            "Decent academic performance"
        )

    else:
        explanation.append(
            "Academic score can improve"
        )

    # SKILLS ANALYSIS
    if len(skills) >= 5:
        explanation.append(
            "Good technical skill diversity"
        )

    elif len(skills) >= 3:
        explanation.append(
            "Moderate technical skills"
        )

    else:
        explanation.append(
            "Need to improve technical skills"
        )

    # PROJECT ANALYSIS
    if len(projects) >= 3:
        explanation.append(
            "Strong project portfolio"
        )

    elif len(projects) >= 1:
        explanation.append(
            "Has practical project exposure"
        )

    else:
        explanation.append(
            "Needs more project work"
        )

    # INTERNSHIP ANALYSIS
    if internships >= 2:
        explanation.append(
            "Strong internship experience"
        )

    elif internships >= 1:
        explanation.append(
            "Has industry exposure"
        )

    else:
        explanation.append(
            "No internship experience yet"
        )

    # HACKATHON ANALYSIS
    if hackathons >= 3:
        explanation.append(
            "Active in hackathons and competitions"
        )

    elif hackathons >= 1:
        explanation.append(
            "Some hackathon participation"
        )

    # FINAL SCORE SUMMARY
    if score >= 80:
        explanation.append(
            "Overall profile is highly competitive"
        )

    elif score >= 60:
        explanation.append(
            "Overall profile is above average"
        )

    else:
        explanation.append(
            "Overall profile needs improvement"
        )

    return explanation
