from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def scoring_test():

    return {
        "success": True,
        "message": "Scoring routes working"
    }
