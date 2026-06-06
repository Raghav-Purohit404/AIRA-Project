"""API callable tests for JD routes."""

from app.api.v1.jd_routes import jd_test


def test_jd_health_route() -> None:
    """JD route should return structured health."""
    response = jd_test()

    assert response["success"] is True
    assert response["message"] == "JD routes working"
