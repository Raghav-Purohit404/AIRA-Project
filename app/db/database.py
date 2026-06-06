"""SQLAlchemy engine and declarative base configuration."""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Declarative base shared by all persistent models."""


def get_database_url() -> str:
    """Return the environment database URL or a local SQLite fallback."""
    configured = os.getenv("AIRA_DATABASE_URL") or os.getenv("DATABASE_URL")
    if configured:
        return configured
    database_path = Path(os.getenv("AIRA_SQLITE_PATH", "aira.db")).resolve()
    return f"sqlite:///{database_path.as_posix()}"


def create_database_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine suitable for SQLite or PostgreSQL."""
    url = database_url or get_database_url()
    options: dict[str, object] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    else:
        options.update({"pool_size": 5, "max_overflow": 10, "pool_recycle": 1800})
    return create_engine(url, **options)


engine = create_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def initialize_database() -> None:
    """Create registered tables for local development and tests."""
    from app.models import audit_log, user  # noqa: F401

    Base.metadata.create_all(bind=engine)
