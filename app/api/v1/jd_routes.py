from fastapi import APIRouter

from app.core.exceptions import ValidationFailedError
from app.models.jd import JobDescription
from app.schemas.jd_schema import JDParseRequest, JDParseResponse, JDSkillMapRequest, JDSkillMapResponse
from app.services.jd.jd_parser import parse_jd
from app.services.jd.jd_skill_mapper import jd_skill_mapper
from app.services.jd.jd_validator import validate_jd_text

router = APIRouter()


@router.get("/")
def jd_test():

    return {
        "success": True,
        "message": "JD routes working"
    }


@router.post("/parse", response_model=JDParseResponse)
def parse_job_description(payload: JDParseRequest) -> JDParseResponse:
    """Validate and deterministically parse a job description into the canonical model."""
    validation = validate_jd_text(payload.text)
    if not validation["is_valid"]:
        raise ValidationFailedError("; ".join(str(error) for error in validation["errors"]))
    parsed = parse_jd(payload.text)
    mapped = jd_skill_mapper.map([*parsed["skills"], *parsed["technologies"]])
    return JDParseResponse(
        job_description=JobDescription(
            role_title="Target Role",
            required_skills=mapped["normalized_skills"],
            education_requirements=parsed["education_requirements"],
            experience_requirements=parsed["experience_requirements"],
            extracted_keywords=mapped["normalized_skills"],
            raw_text=payload.text,
        )
    )


@router.post("/skills/map", response_model=JDSkillMapResponse)
def map_job_skills(payload: JDSkillMapRequest) -> JDSkillMapResponse:
    """Normalize and categorize JD skills using the shared canonical mapper."""
    mapped = jd_skill_mapper.map(payload.skills)
    return JDSkillMapResponse(**mapped)
