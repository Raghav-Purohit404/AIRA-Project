from fastapi import APIRouter

from app.schemas.analytics_schema import (
    AnalyticsResponse,
    CohortAnalyticsRequest,
    StudentComparisonRequest,
    TrendRequest,
)
from app.services.analytics.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/")
def analytics_test() -> dict[str, object]:
    """Return analytics route health."""
    return {"success": True, "message": "Analytics routes working"}


@router.post("/cohort", response_model=AnalyticsResponse)
def cohort_analytics(payload: CohortAnalyticsRequest) -> AnalyticsResponse:
    """Return cohort-level analytics."""
    result = analytics_service.cohort_statistics([student.model_dump() for student in payload.students])
    return AnalyticsResponse(data=result)


@router.post("/compare", response_model=AnalyticsResponse)
def compare_students(payload: StudentComparisonRequest) -> AnalyticsResponse:
    """Compare two scored students."""
    result = analytics_service.compare_students(payload.primary.model_dump(), payload.secondary.model_dump())
    return AnalyticsResponse(data=result)


@router.post("/trend", response_model=AnalyticsResponse)
def analyze_trend(payload: TrendRequest) -> AnalyticsResponse:
    """Return score and profile-growth trend analytics."""
    result = analytics_service.trend([point.model_dump() for point in payload.points])
    return AnalyticsResponse(data=result)
