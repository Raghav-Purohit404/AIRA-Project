from fastapi import APIRouter

from app.schemas.feedback_schema import FeedbackRequest, FeedbackResponse, StoredFeedbackRequest
from app.services.feedback.feedback_engine import FeedbackEngine
from app.services.student_profile_service import student_profile_service

router = APIRouter()
feedback_engine = FeedbackEngine()


@router.get("/")
def feedback_test() -> dict[str, object]:
    """Return feedback route health."""
    return {"success": True, "message": "Feedback routes working"}


@router.post("/profile", response_model=FeedbackResponse)
def generate_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    """Generate feedback for a supplied profile."""
    result = feedback_engine.generate_for_profile(payload.profile, payload.target_skills)
    return FeedbackResponse(feedback=result["feedback"])


@router.post("/profile/{profile_id}", response_model=FeedbackResponse)
def generate_stored_profile_feedback(profile_id: str, payload: StoredFeedbackRequest) -> FeedbackResponse:
    """Generate feedback for a stored profile."""
    profile = student_profile_service.get_profile(profile_id)
    result = feedback_engine.generate_for_profile(profile, payload.target_skills)
    return FeedbackResponse(feedback=result["feedback"])
