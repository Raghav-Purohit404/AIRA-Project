from typing import Dict, List


class ProfileToTextConverter:
    """Converts profile dictionary into semantic text."""

    @staticmethod
    def convert(profile: Dict) -> str:
        parts: List[str] = []

        name = profile.get("name")
        if name:
            parts.append(f"Student name is {name}.")

        department = profile.get("department")
        if department:
            parts.append(f"Department: {department}.")

        cgpa = profile.get("cgpa")
        if cgpa:
            parts.append(f"CGPA is {cgpa}.")

        skills = profile.get("skills", [])
        if skills:
            skill_text = ", ".join(skills)
            parts.append(f"Skilled in {skill_text}.")

        projects = profile.get("projects", [])
        if projects:
            project_text = ", ".join(projects)
            parts.append(f"Worked on projects like {project_text}.")

        internships = profile.get("internships", [])
        if internships:
            internship_text = ", ".join(internships)
            parts.append(f"Internship experience in {internship_text}.")

        achievements = profile.get("achievements", [])
        if achievements:
            achievement_text = ", ".join(achievements)
            parts.append(f"Achievements include {achievement_text}.")

        return " ".join(parts).strip()
