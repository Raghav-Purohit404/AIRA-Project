from fastapi import APIRouter

from app.schemas.scoring_schema import ScoreProfileRequest, ScoreResponse, ScoreStoredProfileRequest
from app.services.aira.aira_engine import aira_engine
from app.services.student_profile_service import student_profile_service

router = APIRouter()


@router.get("/")
def scoring_test() -> dict[str, object]:
    """Return scoring route health."""
    return {"success": True, "message": "Scoring routes working"}


@router.post("/profile", response_model=ScoreResponse)
def score_profile(payload: ScoreProfileRequest) -> ScoreResponse:
    """Score a profile supplied in the request body."""
    score = aira_engine.score_profile(payload.profile, payload.required_skills, payload.ats_weight)
    return ScoreResponse(score=score, breakdown=score.to_flat_dict())


@router.post("/profile/{profile_id}", response_model=ScoreResponse)
def score_stored_profile(profile_id: str, payload: ScoreStoredProfileRequest) -> ScoreResponse:
    """Score a previously stored profile."""
    profile = student_profile_service.get_profile(profile_id)
    score = aira_engine.score_profile(profile, payload.required_skills, payload.ats_weight)
    return ScoreResponse(score=score, breakdown=score.to_flat_dict())
