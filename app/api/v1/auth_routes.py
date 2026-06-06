from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.auth_service import auth_service
from app.core.security import get_current_user
from app.schemas.auth_schema import AuthStatusResponse, LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter()


@router.get("/", response_model=AuthStatusResponse)
def auth_test() -> AuthStatusResponse:
    """Return authentication router health."""
    return AuthStatusResponse(message="Auth routes working")


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest) -> TokenResponse:
    """Register a mock in-memory user and return an access token."""
    return auth_service.register(payload)


@router.post("/login", response_model=TokenResponse)
def login_user(payload: LoginRequest) -> TokenResponse:
    """Authenticate a mock in-memory user and return an access token."""
    return auth_service.login(payload)


@router.get("/me")
def get_me(current_user: Annotated[dict[str, object], Depends(get_current_user)]) -> dict[str, object]:
    """Return the current authenticated token payload."""
    return {"success": True, "user": current_user}
