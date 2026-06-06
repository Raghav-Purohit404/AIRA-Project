from fastapi import APIRouter

from app.services.analytics.analytics_service import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/")
def analytics_test():

    return {
        "success": True,
        "message": "Analytics routes working"
    }
