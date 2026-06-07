"""Benchmark request and response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.benchmark_result import BenchmarkResult


class BenchmarkCaseRequest(BaseModel):
    """Request for running a named benchmark case."""

    suite_name: str = Field(default="default", min_length=2, max_length=120)
    case_names: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BenchmarkRunResponse(BaseModel):
    """Response returned after benchmark execution."""

    success: bool = True
    suite_name: str
    summary: dict[str, Any]
    results: list[BenchmarkResult] = Field(default_factory=list)


class BenchmarkStatusResponse(BaseModel):
    """Status response for benchmark availability."""

    success: bool = True
    available_suites: list[str]
    thresholds: dict[str, float]
