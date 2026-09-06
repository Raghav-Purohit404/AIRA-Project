"""End-to-end coverage for AIRA's grounded resume-to-PDF pipeline.

This file intentionally uses only local fakes for LLM modes; it never requires Ollama.
"""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from app.models.certifications import Certification
from app.models.student_profile import StudentProfile
from app.services.llm_local.hallucination_guard import GroundingResult
from app.services.llm_local.pipeline import LLMPipelineResult
from app.services.resume.pdf_service import PDFService
from app.services.resume.resume_generator import ResumeGenerator


def _profile() -> StudentProfile:
    return StudentProfile.model_validate({
        "id": "resume-test", "basic_info": {"full_name": "Aira Candidate", "email": "aira@example.edu", "phone": "+91-9000000000", "department": "Computer Science", "batch_year": 2027, "location": "Bengaluru, India", "github_url": "https://github.com/aira-candidate"},
        "academic": {"degree": "Bachelor of Engineering", "department": "Computer Science", "institution": "A Very Long Institute of Advanced Engineering and Applied Technology", "location": "Bengaluru, India", "start_year": 2023, "graduation_year": 2027, "cgpa": 8.7},
        "skills": [{"name": "Python"}, {"name": "JS"}, {"name": "Postgres"}, {"name": "FastAPI"}, {"name": "Docker"}],
        "projects": [{"title": "Adaptive Resume Platform", "description": "Built a FastAPI platform that creates machine-readable resumes from validated student profiles. Implemented content-aware layout behavior for long entries.", "technologies": ["Python", "FastAPI", "Postgres", "Docker"], "outcome": "Preserved validated candidate content in generated resume artifacts.", "repository_url": "https://github.com/aira-candidate/adaptive-resume"}],
        "internships": [{"company": "Long Named Recruitment Technology Organization", "role": "Software Engineering Intern", "location": "Remote", "start_date": "2026-05-01", "end_date": "2026-08-01", "description": "Implemented REST API endpoints and SQL query improvements for recruiting workflows.", "technologies": ["Python", "FastAPI", "PostgreSQL"]}],
        "achievements": [{"title": "Campus Hackathon Winner", "category": "technical", "description": "Won for a profile-ranking prototype."}],
        "publications": [{"title": "Grounded Resume Generation", "authors": ["Aira Candidate"], "venue": "Student Research Review", "year": 2026, "doi": "10.0000/aira.resume", "url": "https://example.edu/research/aira-resume"}],
    })


class _FakeLLM:
    def __init__(self, mode: str) -> None:
        self.mode = mode

    def run_skill_pipeline(self, _source: str, _required: list[str]) -> LLMPipelineResult:
        return LLMPipelineResult(success=True, mode=self.mode, skills={"technical_skills": ["Python", "FastAPI"], "frameworks": ["FastAPI"], "tools": [], "programming_languages": ["Python"], "cloud_technologies": []}, scored_skills=[], grounding=GroundingResult(supported=True, confidence=1.0), response={}, error="offline" if self.mode == "deterministic_fallback" else None)


def _render(profile: StudentProfile, tmp_path: Path, *, llm_mode: str = "deterministic_fallback", jd: str | None = None, use_llm: bool = True) -> tuple[dict[str, object], str]:
    generated = ResumeGenerator(llm_pipeline=_FakeLLM(llm_mode)).generate_from_profile(profile, job_description=jd, use_llm_enrichment=use_llm)
    target = tmp_path / f"{profile.id}.pdf"
    PDFService().generate_pdf(str(generated["html"]), resume=generated["resume"], output_path=target)
    assert target.exists() and target.stat().st_size > 0
    reader = PdfReader(str(target))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert len(reader.pages) >= 1
    return generated, text


def test_resume_pipeline_minimal_and_normal_profiles(tmp_path: Path) -> None:
    minimal = _profile().model_copy(update={"skills": [], "projects": [], "internships": [], "achievements": [], "publications": []}, deep=True)
    generated, text = _render(minimal, tmp_path, use_llm=False)
    assert "Aira Candidate" in text and "Education" in text
    assert "Professional Summary" not in text and "Certifications" not in text
    assert generated["ats"]["ats_score"] >= 0

    generated, text = _render(_profile(), tmp_path, llm_mode="live_ollama", jd="Backend intern with Python, FastAPI, PostgreSQL, Docker and SQL experience.")
    assert "Technical Skills" in text and "Adaptive Resume Platform" in text and "PostgreSQL" in text and "Research & Publications" in text
    assert 0 <= generated["ats"]["ats_score"] <= 100
    assert generated["llm"]["mode"] == "live_ollama"
    assert "<!doctype html>" in generated["html"].lower()


def test_resume_pipeline_large_content_and_adaptive_survival(tmp_path: Path) -> None:
    profile = _profile().model_copy(deep=True)
    long_description = "Long project evidence sentence with validated implementation detail. " * 28
    profile.projects = [profile.projects[0].model_copy(update={"title": "Extremely Long Project Name for Candidate Content Preservation", "description": long_description}) for _ in range(6)]
    profile.skills.extend([item.model_copy(update={"name": f"Technology {index}"}) for index, item in enumerate([profile.skills[0]] * 18, start=1)])
    profile.certifications = []
    generated, text = _render(profile, tmp_path)
    reader = PdfReader(str(tmp_path / "resume-test.pdf"))
    assert len(reader.pages) >= 2
    assert "Extremely Long Project Name" in text
    assert "Long project evidence sentence" in text
    assert "Technology 18" in text
    assert "Certifications" not in text
    assert generated["llm"]["mode"] == "deterministic_fallback"


def test_resume_pipeline_certifications_missing_fields_and_no_fabrication(tmp_path: Path) -> None:
    profile = _profile().model_copy(deep=True)
    profile.certifications = [
        Certification(name=f"Validated Certification {number}", issuer="AIRA Academy", credential_id=f"ID-{number}")
        for number in range(1, 13)
    ]
    generated, text = _render(profile, tmp_path)
    assert "Certifications" in text and "Validated Certification 12" in text
    assert "Kubernetes" not in text and "TensorFlow" not in text
    assert "Government ID" not in text and "Marital Status" not in text
    assert generated["resume"]["candidate"]["email"] == "aira@example.edu"
