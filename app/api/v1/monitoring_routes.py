from fastapi import APIRouter

from app.services.monitoring.monitoring_service import MonitoringService

router = APIRouter()
monitoring_service = MonitoringService()


@router.get("/")
def monitoring_test() -> dict[str, object]:
    """Return runtime monitoring details."""
    return monitoring_service.snapshot()
