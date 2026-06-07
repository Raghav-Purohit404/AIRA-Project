"""Benchmark result domain models."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class BenchmarkMetric(BaseModel):
    """A named benchmark metric."""

    name: str = Field(min_length=2, max_length=120)
    value: float
    threshold: float | None = None
    passed: bool | None = None


class BenchmarkResult(BaseModel):
    """Structured benchmark execution result."""

    benchmark_name: str = Field(min_length=2, max_length=160)
    execution_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = Field(ge=0.0)
    accuracy: float | None = Field(default=None, ge=0.0, le=1.0)
    passed: bool = True
    metrics: list[BenchmarkMetric] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
