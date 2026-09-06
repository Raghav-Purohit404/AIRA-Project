"""Resume PDF endpoints built on the canonical AIRA profile pipeline."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.environment import settings
from app.models.student_profile import StudentProfile
from app.services.resume.pdf_service import PDFService
from app.services.resume.resume_generator import ResumeGenerator
from app.services.student_profile_service import student_profile_service
from app.utils.file_manager import build_safe_filename

router = APIRouter()
resume_generator = ResumeGenerator()
pdf_service = PDFService()


class ResumeRequest(BaseModel):
    """Options shared by stored-profile and supplied-profile PDF generation."""

    template: str = Field(default="ats", pattern=r"^(ats|modern|academic)$")
    job_description: str | None = Field(default=None, max_length=20000)
    use_llm_enrichment: bool = False


class ResumeGenerateRequest(ResumeRequest):
    """Validated structured profile request for the canonical /resume/generate endpoint."""

    profile: StudentProfile


@router.get("/")
def resume_test() -> dict[str, object]:
    return {"success": True, "message": "Resume routes working"}


@router.post("/profile/{profile_id}")
def generate_resume(profile_id: str, payload: ResumeRequest) -> dict[str, object]:
    """Return canonical content, HTML intermediate, and ATS metadata for a stored profile."""
    profile = student_profile_service.get_profile(profile_id)
    return resume_generator.generate_from_profile(profile, payload.template, payload.job_description, use_llm_enrichment=payload.use_llm_enrichment)


@router.post("/profile/{profile_id}/pdf", response_class=FileResponse)
def generate_resume_pdf(profile_id: str, payload: ResumeRequest) -> FileResponse:
    """Generate the final PDF artifact for a stored profile and stream it as the primary output."""
    profile = student_profile_service.get_profile(profile_id)
    return _pdf_response(profile, payload)


@router.post("/generate", response_class=FileResponse)
def generate_resume_from_profile(payload: ResumeGenerateRequest) -> FileResponse:
    """Generate the final PDF from a validated structured profile without persisting it first."""
    return _pdf_response(payload.profile, payload)


def _pdf_response(profile: StudentProfile, payload: ResumeRequest) -> FileResponse:
    generated = resume_generator.generate_from_profile(profile, payload.template, payload.job_description, use_llm_enrichment=payload.use_llm_enrichment)
    filename = build_safe_filename(f"{profile.basic_info.full_name.replace(' ', '_')}_{profile.id}_resume.pdf")
    output_path = Path(settings.resume_output_dir) / filename
    rendered = pdf_service.generate_pdf(str(generated["html"]), resume=generated["resume"], output_path=output_path)
    response = FileResponse(path=str(rendered["pdf_path"]), media_type="application/pdf", filename=filename)
    response.headers["X-AIRA-ATS-Score"] = str(generated["ats"]["ats_score"])
    response.headers["X-AIRA-Resume-Path"] = str(rendered["pdf_path"])
    return response
