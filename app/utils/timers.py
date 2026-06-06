"""Timing helpers for instrumentation and benchmarks."""

from __future__ import annotations

from contextlib import contextmanager
from functools import wraps
from time import perf_counter
from typing import Any, Callable, Iterator, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@contextmanager
def elapsed_timer(label: str | None = None) -> Iterator[dict[str, float | str | None]]:
    """Measure elapsed time in seconds for a code block."""
    result: dict[str, float | str | None] = {"label": label, "elapsed_seconds": 0.0, "elapsed_ms": 0.0}
    start = perf_counter()
    try:
        yield result
    finally:
        elapsed_seconds = perf_counter() - start
        result["elapsed_seconds"] = round(elapsed_seconds, 6)
        result["elapsed_ms"] = round(elapsed_seconds * 1000.0, 3)


def timed(func: F) -> F:
    """Decorate a function so it returns timing metadata with its result."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
        start = perf_counter()
        result = func(*args, **kwargs)
        elapsed_seconds = perf_counter() - start
        return {
            "result": result,
            "elapsed_seconds": round(elapsed_seconds, 6),
            "elapsed_ms": round(elapsed_seconds * 1000.0, 3),
        }

    return wrapper  # type: ignore[return-value]


def benchmark_callable(func: Callable[..., Any], *args: Any, iterations: int = 1, **kwargs: Any) -> dict[str, Any]:
    """Run a callable repeatedly and return benchmark timing statistics."""
    if iterations <= 0:
        raise ValueError("Iterations must be greater than zero.")

    latencies_ms: list[float] = []
    last_result: Any = None
    for _ in range(iterations):
        start = perf_counter()
        last_result = func(*args, **kwargs)
        latencies_ms.append(round((perf_counter() - start) * 1000.0, 3))

    return {
        "iterations": iterations,
        "min_ms": min(latencies_ms),
        "max_ms": max(latencies_ms),
        "avg_ms": round(sum(latencies_ms) / iterations, 3),
        "latencies_ms": latencies_ms,
        "last_result": last_result,
    }
