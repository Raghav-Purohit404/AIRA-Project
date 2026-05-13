from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def monitoring_test():

    return {
        "success": True,
        "message": "Monitoring routes working"
    }