"""Grounded projection of validated AIRA profiles into resume content."""

from __future__ import annotations

from datetime import date
from typing import Any

from app.models.jd import JobDescription
from app.models.student_profile import StudentProfile
from app.services.jd.jd_parser import parse_jd
from app.services.jd.jd_skill_mapper import jd_skill_mapper
from app.services.llm_local.pipeline import LocalLLMPipeline
from app.services.resume.ats_optimizer import ATSOptimizer, ats_optimizer
from app.services.resume.template_engine import render_resume_html
from app.utils.validators import validate_email


class ResumeGenerator:
    """Build canonical, evidence-backed resume content; never render raw model output."""

    def __init__(self, llm_pipeline: LocalLLMPipeline | None = None, optimizer: ATSOptimizer | None = None) -> None:
        self.llm_pipeline = llm_pipeline or LocalLLMPipeline()
        self.optimizer = optimizer or ats_optimizer
        self.skill_mapper = jd_skill_mapper

    def generate_json(self, profile: dict[str, Any]) -> dict[str, Any]:
        """Maintain compatibility for legacy dictionary callers with validated input only."""
        candidate = {"name": str(profile.get("name", "")).strip(), "email": str(profile.get("email", "")).strip(), "phone": str(profile.get("phone", "")).strip()}
        if candidate["email"]:
            candidate["email"] = validate_email(candidate["email"])
        return {"candidate": candidate, "sections": {"education": profile.get("education", []), "skills": {"Other": profile.get("skills", [])} if profile.get("skills") else {}, "projects": profile.get("projects", []), "experience": profile.get("internships", []), "achievements": profile.get("achievements", [])}}

    def generate_html(self, profile: dict[str, Any]) -> dict[str, Any]:
        resume = self.generate_json(profile)
        return {"success": True, "resume": resume, "html": render_resume_html(resume)}

    def generate_from_profile(self, profile: StudentProfile, template: str = "ats", job_description: str | JobDescription | None = None, *, use_llm_enrichment: bool = False) -> dict[str, Any]:
        """Validate, normalize, prioritize, and render an ATS-safe HTML intermediate."""
        self._validate_profile(profile)
        jd_skills = self._jd_skills(job_description)
        resume, llm_metadata = self._project(profile, jd_skills, use_llm_enrichment)
        html = render_resume_html(resume, template=template)
        ats = self.optimizer.analyze_against_jd(html, job_description)
        return {"success": True, "resume": resume, "html": html, "ats": ats, "llm": llm_metadata}

    def _validate_profile(self, profile: StudentProfile) -> None:
        if not profile.basic_info.full_name.strip():
            raise ValueError("A resume requires a full name.")
        validate_email(profile.basic_info.email)

    def _jd_skills(self, job_description: str | JobDescription | None) -> list[str]:
        if isinstance(job_description, JobDescription):
            skills = [*job_description.required_skills, *job_description.preferred_skills]
        elif isinstance(job_description, str) and job_description.strip():
            parsed = parse_jd(job_description)
            skills = [*parsed.get("skills", []), *parsed.get("technologies", [])]
        else:
            skills = []
        return self.skill_mapper.normalize_skills([str(skill) for skill in skills])

    def _project(self, profile: StudentProfile, jd_skills: list[str], use_llm: bool) -> tuple[dict[str, Any], dict[str, Any]]:
        evidence_skills = [*profile.skill_names(), *(tech for project in profile.projects for tech in project.technologies), *(tech for item in profile.internships for tech in item.technologies)]
        canonical_skills = self.skill_mapper.normalize_skills(evidence_skills)
        llm_metadata: dict[str, Any] = {"mode": "profile_backed", "grounded": True, "added_skills": []}
        if use_llm:
            source = self._profile_evidence(profile)
            result = self.llm_pipeline.run_skill_pipeline(source, jd_skills)
            grounded = [skill for values in result.skills.values() for skill in values] if result.grounding.supported else []
            # Layer 3: only grounded terms may join the canonical representation.
            added = self.skill_mapper.normalize_skills(grounded)
            canonical_skills = self.skill_mapper.normalize_skills([*canonical_skills, *added])
            llm_metadata = {"mode": result.mode, "grounded": result.grounding.supported, "added_skills": added, "error": result.error}
        priority = {skill.casefold(): index for index, skill in enumerate(jd_skills)}
        canonical_skills.sort(key=lambda skill: (priority.get(skill.casefold(), len(priority)), skill.casefold()))
        sections = {
            "summary": self._summary(profile, canonical_skills),
            "skills": self._group_skills(canonical_skills),
            "education": self._education(profile),
            "experience": self._experience(profile, priority),
            "projects": self._projects(profile, priority),
            "certifications": self._certifications(profile),
            "achievements": self._achievements(profile),
            "research": self._research(profile),
            "leadership": self._leadership(profile),
        }
        return {"candidate": self._candidate(profile), "profile_completeness": profile.completeness_score(), "sections": {key: value for key, value in sections.items() if value}}, llm_metadata

    def _candidate(self, profile: StudentProfile) -> dict[str, str]:
        info = profile.basic_info
        return {"name": info.full_name, "email": info.email, "phone": info.phone or "", "location": info.location or "", "linkedin": info.linkedin_url or "", "github": info.github_url or "", "portfolio": info.portfolio_url or ""}

    def _summary(self, profile: StudentProfile, skills: list[str]) -> str:
        if not (skills or profile.projects or profile.internships):
            return ""
        subject = f"{profile.academic.department} student pursuing {profile.academic.degree}"
        evidence: list[str] = []
        if skills:
            evidence.append(f"with skills in {', '.join(skills[:4])}")
        if profile.internships:
            evidence.append(f"and {len(profile.internships)} internship experience{'s' if len(profile.internships) != 1 else ''}")
        elif profile.projects:
            evidence.append(f"and {len(profile.projects)} project{'s' if len(profile.projects) != 1 else ''}")
        return f"{subject} {' '.join(evidence)}.".replace("  ", " ")

    def _group_skills(self, skills: list[str]) -> dict[str, list[str]]:
        categories = {"Languages": [], "Frameworks": [], "Databases": [], "ML/AI": [], "Tools & Cloud": [], "Other": []}
        mapping = {"Python": "Languages", "Java": "Languages", "JavaScript": "Languages", "TypeScript": "Languages", "C++": "Languages", "C#": "Languages", "SQL": "Databases", "PostgreSQL": "Databases", "MongoDB": "Databases", "Redis": "Databases", "FastAPI": "Frameworks", "Django": "Frameworks", "Flask": "Frameworks", "React": "Frameworks", "Angular": "Frameworks", "Machine Learning": "ML/AI", "Artificial Intelligence": "ML/AI", "Deep Learning": "ML/AI", "Natural Language Processing": "ML/AI", "Docker": "Tools & Cloud", "Kubernetes": "Tools & Cloud", "Git": "Tools & Cloud", "Linux": "Tools & Cloud", "AWS": "Tools & Cloud", "Azure": "Tools & Cloud", "GCP": "Tools & Cloud"}
        for skill in skills:
            categories[mapping.get(skill, "Other")].append(skill)
        return {category: values for category, values in categories.items() if values}

    def _education(self, profile: StudentProfile) -> list[dict[str, Any]]:
        record = profile.academic
        title = " in ".join(value for value in (record.degree, record.department) if value)
        meta_parts = [value for value in (record.institution, record.location) if value]
        dates = f"{record.start_year}-" if record.start_year else ""
        dates += str(record.graduation_year)
        bullets = [f"{dates} | CGPA: {record.cgpa:.2f}/10"]
        return [{"title": title, "meta": " | ".join(meta_parts), "bullets": bullets}]

    def _experience(self, profile: StudentProfile, priority: dict[str, int]) -> list[dict[str, Any]]:
        entries = []
        for item in sorted(profile.internships, key=lambda value: -self._relevance(value.technologies, priority)):
            dates = f"{item.start_date.strftime('%b %Y')} - {(item.end_date or date.today()).strftime('%b %Y')}"
            meta = " | ".join(value for value in (item.company, item.location, dates) if value)
            bullets = self._sentences(item.description)
            if item.technologies:
                bullets.append(f"Technologies: {', '.join(self.skill_mapper.normalize_skills(item.technologies))}")
            entries.append({"title": item.role, "meta": meta, "bullets": bullets})
        return entries

    def _projects(self, profile: StudentProfile, priority: dict[str, int]) -> list[dict[str, Any]]:
        entries = []
        for item in sorted(profile.projects, key=lambda value: -self._relevance(value.technologies, priority)):
            bullets = self._sentences(item.description)
            if item.role:
                bullets.insert(0, f"Role: {item.role}")
            if item.technologies:
                bullets.append(f"Technologies: {', '.join(self.skill_mapper.normalize_skills(item.technologies))}")
            if item.outcome:
                bullets.append(item.outcome)
            entries.append({"title": item.title, "meta": item.date or "", "bullets": bullets, "links": [url for url in (item.repository_url, item.deployment_url) if url]})
        return entries

    def _certifications(self, profile: StudentProfile) -> list[dict[str, Any]]:
        return [{"title": item.name, "meta": " | ".join(value for value in (item.issuer, item.issue_date.strftime('%b %Y') if item.issue_date else "") if value), "bullets": [f"Credential ID: {item.credential_id}"] if item.credential_id else [], "links": [item.credential_url] if item.credential_url else []} for item in profile.certifications]

    def _achievements(self, profile: StudentProfile) -> list[dict[str, Any]]:
        items = [{"title": item.title, "meta": " | ".join(value for value in (item.issuer, item.awarded_on.strftime('%b %Y') if item.awarded_on else "") if value), "bullets": [item.description] if item.description else []} for item in profile.achievements]
        items.extend({"title": item.name, "meta": " | ".join(value for value in (item.organizer, item.position) if value), "bullets": [f"Project: {item.project_title}"] if item.project_title else []} for item in profile.hackathons)
        return items

    def _leadership(self, profile: StudentProfile) -> list[dict[str, Any]]:
        return [{"title": item.title, "meta": item.leadership_role or item.activity_type.value.title(), "bullets": item.achievements} for item in profile.extracurriculars]

    def _research(self, profile: StudentProfile) -> list[dict[str, Any]]:
        return [{"title": item.title, "meta": " | ".join(value for value in (item.venue, str(item.year) if item.year else "") if value), "bullets": ([", ".join(item.authors)] if item.authors else []) + ([f"DOI: {item.doi}"] if item.doi else []), "links": [item.url] if item.url else []} for item in profile.publications]

    @staticmethod
    def _sentences(text: str) -> list[str]:
        cleaned = " ".join(text.split())
        if not cleaned:
            return []
        chunks = [part.strip() for part in cleaned.replace(". ", ".\n").splitlines() if part.strip()]
        if len(chunks) <= 4:
            return chunks
        size = (len(chunks) + 3) // 4
        return [" ".join(chunks[index : index + size]) for index in range(0, len(chunks), size)]

    def _profile_evidence(self, profile: StudentProfile) -> str:
        return " ".join(str(value) for value in profile.model_dump(mode="json").values())

    def _relevance(self, skills: list[str], priority: dict[str, int]) -> float:
        return sum(1.0 / (1 + priority.get(self.skill_mapper.normalize_skill(skill).casefold(), 999)) for skill in skills)
