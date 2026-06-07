"""ATS compatibility analysis for generated or supplied resumes."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any


class ATSOptimizer:
    """Analyze resume content and recommend ATS improvements."""

    RECOMMENDED_SECTIONS = ["summary", "skills", "experience", "projects", "education"]

    def analyze(self, resume_text: str, target_skills: list[str] | None = None) -> dict[str, Any]:
        """Return keyword density, section, formatting, and skill-gap analysis."""
        normalized_text = resume_text.casefold()
        target_skills = target_skills or []
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]{1,}", normalized_text)
        counts = Counter(tokens)
        keyword_density = {
            skill: round(counts[skill.casefold()] / max(len(tokens), 1), 4)
            for skill in target_skills
        }
        missing_skills = [skill for skill in target_skills if skill.casefold() not in normalized_text]
        section_order = self._section_recommendations(normalized_text)
        formatting_warnings = self._formatting_warnings(resume_text)
        return {
            "success": True,
            "keyword_density": keyword_density,
            "missing_skills": missing_skills,
            "section_order_recommendations": section_order,
            "formatting_warnings": formatting_warnings,
            "ats_score": self._score(keyword_density, missing_skills, formatting_warnings),
        }

    def _section_recommendations(self, normalized_text: str) -> list[str]:
        """Return missing recommended sections."""
        return [section for section in self.RECOMMENDED_SECTIONS if section not in normalized_text]

    def _formatting_warnings(self, resume_text: str) -> list[str]:
        """Return ATS formatting warnings."""
        warnings: list[str] = []
        if len(resume_text) > 12000:
            warnings.append("Resume content is long for a first-pass ATS parse.")
        if re.search(r"[│┌┐└┘]", resume_text):
            warnings.append("Table-like box characters can reduce ATS parsing accuracy.")
        if resume_text.count("\t") > 10:
            warnings.append("Excessive tab formatting can reduce ATS parsing accuracy.")
        return warnings

    def _score(self, keyword_density: dict[str, float], missing_skills: list[str], warnings: list[str]) -> float:
        """Calculate a bounded ATS compatibility score."""
        base = 100.0
        base -= len(missing_skills) * 8.0
        base -= len(warnings) * 5.0
        if keyword_density and all(value == 0.0 for value in keyword_density.values()):
            base -= 10.0
        return round(max(0.0, min(100.0, base)), 2)


ats_optimizer = ATSOptimizer()
