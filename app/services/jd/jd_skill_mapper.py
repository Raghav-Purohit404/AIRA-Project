"""Normalize extracted job-description skills into canonical categories."""

from __future__ import annotations

from collections import defaultdict

from app.core.constants import CANONICAL_SKILL_ALIASES


SKILL_CATEGORIES: dict[str, set[str]] = {
    "programming": {"Python", "JavaScript", "TypeScript", "Java", "C++", "SQL"},
    "backend": {"FastAPI", "Django", "Flask", "Node.js", "REST", "PostgreSQL", "Redis"},
    "ai_ml": {"Machine Learning", "Artificial Intelligence", "Deep Learning", "Natural Language Processing"},
    "devops": {"Docker", "Kubernetes", "Git", "CI/CD", "Linux"},
    "frontend": {"React", "Angular", "Vue", "HTML", "CSS"},
}


class JDSkillMapper:
    """Map raw extracted JD skills to normalized names and categories."""

    def normalize_skill(self, skill: str) -> str:
        """Return a canonical skill name."""
        normalized = " ".join(skill.replace("_", " ").strip().split())
        alias_key = normalized.casefold()
        return CANONICAL_SKILL_ALIASES.get(alias_key, normalized)

    def normalize_skills(self, skills: list[str]) -> list[str]:
        """Normalize and deduplicate a skill list."""
        result: list[str] = []
        seen: set[str] = set()
        for skill in skills:
            canonical = self.normalize_skill(skill)
            key = canonical.casefold()
            if canonical and key not in seen:
                seen.add(key)
                result.append(canonical)
        return result

    def categorize(self, skills: list[str]) -> dict[str, list[str]]:
        """Group normalized skills by broad recruitment category."""
        categories: dict[str, list[str]] = defaultdict(list)
        for skill in self.normalize_skills(skills):
            matched = False
            for category, known_skills in SKILL_CATEGORIES.items():
                if skill in known_skills:
                    categories[category].append(skill)
                    matched = True
            if not matched:
                categories["other"].append(skill)
        return dict(categories)

    def map(self, skills: list[str]) -> dict[str, object]:
        """Return normalized skills and category groupings."""
        normalized = self.normalize_skills(skills)
        return {"normalized_skills": normalized, "categories": self.categorize(normalized)}


jd_skill_mapper = JDSkillMapper()
