"""Password hashing helpers for local, non-database authentication flows."""

from __future__ import annotations

import hashlib
import hmac
import os
from base64 import urlsafe_b64decode, urlsafe_b64encode


PBKDF2_ITERATIONS = 260_000
SALT_BYTES = 16


def _encode(value: bytes) -> str:
    """Return URL-safe base64 text without padding."""
    return urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def _decode(value: str) -> bytes:
    """Decode URL-safe base64 text that may not include padding."""
    padding = "=" * (-len(value) % 4)
    return urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256."""
    if not password:
        raise ValueError("Password must not be empty.")

    salt = os.urandom(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, password_hash: str) -> bool:
    """Return True when a plain password matches a stored password hash."""
    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_text)
        salt = _decode(salt_text)
        expected_digest = _decode(digest_text)
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(actual_digest, expected_digest)
