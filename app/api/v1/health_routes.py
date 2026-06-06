from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health_check() -> dict[str, object]:
    """Return service health status."""
    return {
        "success": True,
        "status": "healthy"
    }
