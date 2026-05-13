from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def auth_test():

    return {
        "success": True,
        "message": "Auth routes working"
    }
