from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def faculty_test():

    return {
        "success": True,
        "message": "Faculty routes working"
    }
