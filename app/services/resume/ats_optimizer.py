"""ATS compatibility analysis for generated or supplied resumes."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.models.jd import JobDescription
from app.services.jd.jd_parser import parse_jd
from app.services.jd.jd_skill_mapper import jd_skill_mapper


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
        matched_skills = [skill for skill in target_skills if skill.casefold() in normalized_text]
        completeness = round(
            100.0 * (len(self.RECOMMENDED_SECTIONS) - len(section_order)) / len(self.RECOMMENDED_SECTIONS), 2
        )
        return {
            "success": True,
            "keyword_density": keyword_density,
            "missing_skills": missing_skills,
            "matched_skills": matched_skills,
            "required_skill_coverage": round(100.0 * len(matched_skills) / max(len(target_skills), 1), 2),
            "section_completeness": completeness,
            "section_order_recommendations": section_order,
            "formatting_warnings": formatting_warnings,
            "ats_score": self._score(keyword_density, missing_skills, formatting_warnings),
        }

    def analyze_against_jd(
        self,
        resume_text: str,
        job_description: str | JobDescription | None,
    ) -> dict[str, Any]:
        """Assess ATS compatibility against a supplied JD without adding unsupported terms."""
        if job_description is None:
            return self.analyze(resume_text)
        if isinstance(job_description, JobDescription):
            raw_skills = [*job_description.required_skills, *job_description.preferred_skills]
            role_title = job_description.role_title
        else:
            parsed = parse_jd(job_description)
            raw_skills = [*parsed.get("skills", []), *parsed.get("technologies", [])]
            role_title = ""
        target_skills = jd_skill_mapper.normalize_skills([str(skill) for skill in raw_skills])
        result = self.analyze(resume_text, target_skills)
        result["job_title"] = role_title
        result["target_skills"] = target_skills
        return result

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
