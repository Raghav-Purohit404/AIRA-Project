from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_local.skill_extractor import extract_skills

router = APIRouter()


class SkillExtractionRequest(BaseModel):
    text: str


@router.post("/extract-skills")
def extract_student_skills(data: SkillExtractionRequest):

    skills = extract_skills(data.text)

    return {
        "success": True,
        "skills": skills
    }
