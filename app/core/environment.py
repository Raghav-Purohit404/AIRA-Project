"""Environment loading and validation helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def env_str(name: str, default: str) -> str:
    """Return a stripped environment variable or a default."""
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


def env_int(name: str, default: int, *, minimum: int | None = None) -> int:
    """Return an integer environment variable with optional lower bound."""
    try:
        value = int(env_str(name, str(default)))
    except ValueError:
        value = default
    return max(value, minimum) if minimum is not None else value


def env_float(name: str, default: float, *, minimum: float | None = None) -> float:
    """Return a float environment variable with optional lower bound."""
    try:
        value = float(env_str(name, str(default)))
    except ValueError:
        value = default
    return max(value, minimum) if minimum is not None else value


def env_bool(name: str, default: bool = False) -> bool:
    """Return a boolean environment variable."""
    value = env_str(name, str(default)).casefold()
    return value in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppEnvironment:
    """Typed runtime configuration used by application modules."""

    environment: str
    log_level: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    ollama_url: str
    ollama_model: str
    ollama_timeout_seconds: float
    database_url: str
    faiss_index_path: Path
    faiss_metadata_path: Path

    @property
    def is_production(self) -> bool:
        """Return whether the app is running in production mode."""
        return self.environment.casefold() == "production"

    def validate(self) -> list[str]:
        """Return configuration validation warnings."""
        warnings: list[str] = []
        if self.is_production and "change-before-production" in self.jwt_secret_key:
            warnings.append("JWT secret key must be changed for production.")
        if self.access_token_expire_minutes <= 0:
            warnings.append("Access token expiry must be positive.")
        if not self.database_url:
            warnings.append("Database URL is empty.")
        return warnings


def load_environment() -> AppEnvironment:
    """Load application environment with safe local defaults."""
    return AppEnvironment(
        environment=env_str("ENVIRONMENT", "development"),
        log_level=env_str("LOG_LEVEL", "INFO").upper(),
        jwt_secret_key=env_str("JWT_SECRET_KEY", "aira-local-development-secret-change-before-production"),
        jwt_algorithm=env_str("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60, minimum=1),
        ollama_url=env_str("OLLAMA_URL", "http://localhost:11434"),
        ollama_model=env_str("OLLAMA_MODEL", "phi3:3.8b"),
        ollama_timeout_seconds=env_float("OLLAMA_TIMEOUT_SECONDS", 30.0, minimum=1.0),
        database_url=env_str("AIRA_DATABASE_URL", env_str("DATABASE_URL", "sqlite:///aira.db")),
        faiss_index_path=Path(env_str("FAISS_INDEX_PATH", "data/faiss/aira.index")),
        faiss_metadata_path=Path(env_str("FAISS_METADATA_PATH", "data/faiss/metadata.json")),
    )


settings = load_environment()
