"""In-memory authentication service used until persistence is introduced."""

from __future__ import annotations

from fastapi import HTTPException, status

from app.auth.jwt_handler import create_access_token
from app.auth.password_utils import hash_password, verify_password
from app.schemas.auth_schema import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class InMemoryAuthService:
    """Manage mock users without introducing fake database code."""

    def __init__(self) -> None:
        self._users: dict[str, dict[str, str]] = {}

    def _to_user_response(self, user: dict[str, str]) -> UserResponse:
        """Convert stored user data to a public response schema."""
        return UserResponse(email=user["email"], full_name=user["full_name"], role=user["role"])

    def register(self, payload: RegisterRequest) -> TokenResponse:
        """Register a user and return a bearer token."""
        normalized_email = payload.email.lower()
        if normalized_email in self._users:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

        self._users[normalized_email] = {
            "email": normalized_email,
            "full_name": payload.full_name,
            "role": payload.role.value,
            "password_hash": hash_password(payload.password),
        }
        return self._build_token_response(self._users[normalized_email])

    def login(self, payload: LoginRequest) -> TokenResponse:
        """Authenticate a user and return a bearer token."""
        normalized_email = payload.email.lower()
        user = self._users.get(normalized_email)
        if user is None or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
        return self._build_token_response(user)

    def _build_token_response(self, user: dict[str, str]) -> TokenResponse:
        """Create a token response for a stored user."""
        token = create_access_token(
            subject=user["email"],
            claims={"role": user["role"], "full_name": user["full_name"]},
        )
        return TokenResponse(access_token=token, user=self._to_user_response(user))


auth_service = InMemoryAuthService()
