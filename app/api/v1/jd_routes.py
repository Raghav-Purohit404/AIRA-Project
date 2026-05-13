from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def jd_test():

    return {
        "success": True,
        "message": "JD routes working"
    }