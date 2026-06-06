"""Small signed token helper used until a full auth provider is integrated."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime, timedelta, timezone
from typing import Any


DEFAULT_EXPIRES_MINUTES = 60
JWT_SECRET_ENV = "AIRA_JWT_SECRET"
_FALLBACK_SECRET = "aira-development-secret"


def _encode_json(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _decode_json(value: str) -> dict[str, Any]:
    padding = "=" * (-len(value) % 4)
    raw = urlsafe_b64decode(value + padding)
    decoded = json.loads(raw.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("Token payload must be a JSON object.")
    return decoded


def _sign(message: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def get_jwt_secret() -> str:
    """Return the configured token signing secret."""
    return os.getenv(JWT_SECRET_ENV, _FALLBACK_SECRET)


def create_access_token(
    subject: str,
    claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed bearer token for a subject."""
    if not subject:
        raise ValueError("Token subject is required.")

    now = datetime.now(timezone.utc)
    expires_at = now + (expires_delta or timedelta(minutes=DEFAULT_EXPIRES_MINUTES))
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    if claims:
        payload.update(claims)

    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{_encode_json(header)}.{_encode_json(payload)}"
    return f"{signing_input}.{_sign(signing_input, get_jwt_secret())}"


def decode_access_token(token: str) -> dict[str, Any]:
    """Validate and decode a signed bearer token."""
    try:
        header_text, payload_text, signature = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid token format.") from exc

    signing_input = f"{header_text}.{payload_text}"
    expected_signature = _sign(signing_input, get_jwt_secret())
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("Invalid token signature.")

    header = _decode_json(header_text)
    if header.get("alg") != "HS256":
        raise ValueError("Unsupported token algorithm.")

    payload = _decode_json(payload_text)
    expires_at = int(payload.get("exp", 0))
    if expires_at < int(datetime.now(timezone.utc).timestamp()):
        raise ValueError("Token has expired.")
    return payload
