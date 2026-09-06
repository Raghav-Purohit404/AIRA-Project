"""Conversion of structured profiles into semantic search text."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class ProfileToTextConverter:
    """Convert profile dictionaries or Pydantic models into semantic prose."""

    @classmethod
    def convert(cls, profile: Mapping[str, Any] | Any) -> str:
        """Return normalized, information-rich text for embedding."""
        data = profile.model_dump(mode="json") if hasattr(profile, "model_dump") else dict(profile)
        basic = data.get("basic_info") if isinstance(data.get("basic_info"), Mapping) else data
        academic = data.get("academic") if isinstance(data.get("academic"), Mapping) else data
        parts: list[str] = []

        name = basic.get("full_name") or basic.get("name")
        department = basic.get("department") or academic.get("department")
        cgpa = academic.get("cgpa")
        if name:
            parts.append(f"{name} is a student")
        if department:
            parts.append(f"from {department}")
        if parts:
            parts[-1] = f"{parts[-1]}."
        if cgpa is not None:
            parts.append(f"Academic CGPA: {cgpa}.")

        skills = cls._labels(data.get("skills"), ("name", "skill"))
        if skills:
            parts.append(f"Technical skills include {', '.join(skills)}.")
        projects = cls._labels(data.get("projects"), ("title", "name"))
        if projects:
            parts.append(f"Project experience includes {', '.join(projects)}.")
        internships = cls._labels(data.get("internships"), ("role", "company", "name"))
        if internships:
            parts.append(f"Internship experience includes {', '.join(internships)}.")
        achievements = cls._labels(data.get("achievements"), ("title", "name"))
        if achievements:
            parts.append(f"Achievements include {', '.join(achievements)}.")
        certifications = cls._labels(data.get("certifications"), ("name",))
        if certifications:
            parts.append(f"Certifications include {', '.join(certifications)}.")
        publications = cls._labels(data.get("publications"), ("title", "venue"))
        if publications:
            parts.append(f"Research includes {', '.join(publications)}.")
        activities = cls._labels(data.get("extracurriculars"), ("title", "leadership_role"))
        if activities:
            parts.append(f"Leadership and activities include {', '.join(activities)}.")
        return " ".join(parts).strip()

    @staticmethod
    def _labels(value: Any, keys: tuple[str, ...]) -> list[str]:
        """Extract readable labels from strings or structured items."""
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            return []
        labels: list[str] = []
        for item in value:
            if isinstance(item, str):
                label = item
            elif isinstance(item, Mapping):
                label = " at ".join(str(item[key]) for key in keys if item.get(key))
            else:
                label = str(item)
            normalized = " ".join(label.split())
            if normalized:
                labels.append(normalized)
        return labels
