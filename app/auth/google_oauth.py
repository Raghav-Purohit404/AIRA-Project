"""Google OAuth token verification and local account integration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.auth.jwt_handler import create_access_token


@dataclass(frozen=True)
class GoogleIdentity:
    """Verified identity claims extracted from a Google ID token."""

    subject: str
    email: str
    full_name: str
    picture: str | None = None
    email_verified: bool = True


_google_users: dict[str, dict[str, str | None]] = {}


def verify_google_token(token: str, client_id: str | None = None) -> GoogleIdentity:
    """Verify a Google ID token and return normalized user claims."""
    if not token or not token.strip():
        raise ValueError("Google token is required.")
    audience = client_id or os.getenv("GOOGLE_CLIENT_ID")
    if not audience:
        raise ValueError("GOOGLE_CLIENT_ID is not configured.")

    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token
    except ImportError as exc:
        raise RuntimeError("google-auth is required for Google token verification.") from exc

    claims: dict[str, Any] = id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        audience,
    )
    issuer = claims.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise ValueError("Google token issuer is invalid.")
    email = str(claims.get("email", "")).strip().lower()
    subject = str(claims.get("sub", "")).strip()
    if not email or not subject:
        raise ValueError("Google token is missing required identity claims.")
    if claims.get("email_verified") is False:
        raise ValueError("Google email address is not verified.")
    return GoogleIdentity(
        subject=subject,
        email=email,
        full_name=str(claims.get("name") or email.split("@", 1)[0]).strip(),
        picture=str(claims["picture"]) if claims.get("picture") else None,
    )


def create_google_user(
    identity: GoogleIdentity | dict[str, Any],
    role: str = "student",
) -> dict[str, str | None]:
    """Create or update an OAuth-compatible local user representation."""
    verified = identity if isinstance(identity, GoogleIdentity) else GoogleIdentity(**identity)
    user = _google_users.get(verified.email)
    if user is None:
        user = {
            "id": str(uuid4()),
            "email": verified.email,
            "full_name": verified.full_name,
            "role": role,
            "google_subject": verified.subject,
            "picture": verified.picture,
        }
        _google_users[verified.email] = user
    else:
        user.update(
            {
                "full_name": verified.full_name,
                "google_subject": verified.subject,
                "picture": verified.picture,
            }
        )
    return dict(user)


def google_login_handler(
    token: str,
    role: str = "student",
    client_id: str | None = None,
) -> dict[str, object]:
    """Verify Google identity, upsert the user, and issue an AIRA JWT."""
    identity = verify_google_token(token, client_id)
    user = create_google_user(identity, role)
    access_token = create_access_token(
        subject=str(user["email"]),
        claims={
            "user_id": user["id"],
            "role": user["role"],
            "full_name": user["full_name"],
            "auth_provider": "google",
        },
    )
    return {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
