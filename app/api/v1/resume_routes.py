from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def resume_test():

    return {
        "success": True,
        "message": "Resume routes working"
    }
