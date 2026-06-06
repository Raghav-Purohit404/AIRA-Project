"""Structured resume generation service."""

from __future__ import annotations

from typing import Any

from app.models.student_profile import StudentProfile
from app.services.resume.template_engine import render_resume_html


class ResumeGenerator:
    """Generate structured resume JSON and HTML from profile data."""

    def generate_json(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Return normalized resume JSON from a student profile."""
        return {
            "candidate": {
                "name": profile.get("name", ""),
                "email": profile.get("email", ""),
                "phone": profile.get("phone", ""),
            },
            "sections": {
                "education": profile.get("education", []),
                "skills": profile.get("skills", []),
                "projects": profile.get("projects", []),
                "internships": profile.get("internships", []),
                "achievements": profile.get("achievements", []),
            },
        }

    def generate_html(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Return a structured resume and rendered HTML template."""
        resume = self.generate_json(profile)
        return {"success": True, "resume": resume, "html": render_resume_html(resume)}

    def generate_from_profile(self, profile: StudentProfile, template: str = "ats") -> dict[str, Any]:
        """Generate structured resume JSON and HTML from a StudentProfile."""
        resume = {
            "candidate": {
                "name": profile.basic_info.full_name,
                "email": profile.basic_info.email,
                "phone": profile.basic_info.phone or "",
                "department": profile.basic_info.department,
            },
            "profile_completeness": profile.completeness_score(),
            "sections": {
                "summary": [
                    f"{profile.basic_info.department} student with CGPA {profile.academic.cgpa:.2f} and {len(profile.projects)} project(s)."
                ],
                "education": [
                    f"{profile.academic.degree}, {profile.academic.department}, graduating {profile.academic.graduation_year}, CGPA {profile.academic.cgpa:.2f}"
                ],
                "skills": profile.skill_names(),
                "projects": [
                    f"{project.title}: {project.description}"
                    for project in profile.projects
                ],
                "internships": [
                    f"{internship.role} at {internship.company}"
                    for internship in profile.internships
                ],
                "achievements": [
                    achievement.title for achievement in profile.achievements
                ],
            },
        }
        return {"success": True, "resume": resume, "html": render_resume_html(resume, template=template)}
