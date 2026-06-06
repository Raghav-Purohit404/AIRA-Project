from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.resume.pdf_service import PDFService
from app.services.resume.resume_generator import ResumeGenerator
from app.services.student_profile_service import student_profile_service

router = APIRouter()
resume_generator = ResumeGenerator()
pdf_service = PDFService()


@router.get("/")
def resume_test() -> dict[str, object]:
    """Return resume route health."""
    return {"success": True, "message": "Resume routes working"}


class ResumeRequest(BaseModel):
    """Resume generation options."""

    template: str = Field(default="ats", pattern=r"^(ats|modern|academic)$")


@router.post("/profile/{profile_id}")
def generate_resume(profile_id: str, payload: ResumeRequest) -> dict[str, object]:
    """Generate structured resume JSON and HTML for a stored profile."""
    profile = student_profile_service.get_profile(profile_id)
    return resume_generator.generate_from_profile(profile, template=payload.template)


@router.post("/profile/{profile_id}/pdf")
def generate_resume_pdf(profile_id: str, payload: ResumeRequest) -> dict[str, object]:
    """Generate PDF bytes metadata for a stored profile resume."""
    profile = student_profile_service.get_profile(profile_id)
    html_result = resume_generator.generate_from_profile(profile, template=payload.template)
    pdf_result = pdf_service.generate_pdf(str(html_result["html"]))
    return {
        "success": True,
        "content_type": pdf_result["content_type"],
        "byte_length": len(pdf_result["pdf_bytes"]),
        "html_length": pdf_result["html_length"],
    }
