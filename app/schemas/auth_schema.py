"""Pydantic models for authentication requests and responses."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.permissions import Role


class RegisterRequest(BaseModel):
    """User registration payload for the in-memory auth service."""

    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=100)
    role: Role = Role.STUDENT


class LoginRequest(BaseModel):
    """User login payload."""

    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Public user identity returned by auth endpoints."""

    email: str
    full_name: str
    role: Role


class TokenResponse(BaseModel):
    """Bearer token response."""

    success: bool = True
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthStatusResponse(BaseModel):
    """Simple structured auth status response."""

    success: bool = True
    message: str
