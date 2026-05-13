from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def benchmark_test():

    return {
        "success": True,
        "message": "Benchmark routes working"
    }
