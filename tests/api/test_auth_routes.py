"""API callable tests for auth routes."""

from app.api.v1.auth_routes import auth_test, get_me, login_user, register_user
from app.schemas.auth_schema import LoginRequest, RegisterRequest
from fastapi import HTTPException
import pytest


def test_auth_health_route() -> None:
    """Auth router should return structured health."""
    response = auth_test()

    assert response.success is True


def test_register_login_and_me_flow() -> None:
    """Auth flow should register, login, and decode bearer token payload."""
    email = "route-user@example.com"
    register_response = register_user(
        RegisterRequest(email=email, password="password123", full_name="Route User", role="student")
    )

    assert register_response.success is True
    assert register_response.access_token

    login_response = login_user(LoginRequest(email=email, password="password123"))
    assert login_response.success is True

    me_response = get_me({"sub": email, "role": "student"})
    assert me_response["user"]["sub"] == email


def test_login_rejects_invalid_credentials() -> None:
    """Login should reject wrong passwords."""
    email = "bad-login@example.com"
    register_user(RegisterRequest(email=email, password="password123", full_name="Bad Login", role="student"))

    with pytest.raises(HTTPException) as exc_info:
        login_user(LoginRequest(email=email, password="wrong"))

    assert exc_info.value.status_code == 401
