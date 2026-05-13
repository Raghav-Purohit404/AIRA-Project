from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def feedback_test():

    return {
        "success": True,
        "message": "Feedback routes working"
    }