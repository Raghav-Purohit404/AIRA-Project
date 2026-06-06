"""Conversion helpers for API-safe data structures and models."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime, timezone
from typing import Any

from pydantic import BaseModel


def to_float(value: Any, default: float = 0.0) -> float:
    """Convert a value to float with a safe default."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_serializable(value: Any) -> Any:
    """Convert common Python objects to JSON-serializable structures."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: to_serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_serializable(item) for item in value]
    return value


def dict_to_model(model_type: type[BaseModel], payload: dict[str, Any]) -> BaseModel:
    """Convert a dictionary to a Pydantic model instance."""
    return model_type.model_validate(payload)


def model_to_dict(model: BaseModel, exclude_none: bool = True) -> dict[str, Any]:
    """Convert a Pydantic model to a JSON-ready dictionary."""
    return model.model_dump(mode="json", exclude_none=exclude_none)


def parse_datetime(value: str | datetime) -> datetime:
    """Parse ISO datetime text into a timezone-aware datetime."""
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def format_datetime(value: datetime) -> str:
    """Format a datetime as an ISO-8601 string."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
