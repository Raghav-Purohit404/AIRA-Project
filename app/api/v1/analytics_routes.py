from fastapi import APIRouter

router = APIRouter()
analytics_service = AnalyticsService()


@router.get("/")
def analytics_test():

    return {
        "success": True,
        "message": "Analytics routes working"
    }
