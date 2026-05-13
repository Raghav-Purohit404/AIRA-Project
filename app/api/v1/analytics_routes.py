from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def analytics_test():

    return {
        "success": True,
        "message": "Analytics routes working"
    }
