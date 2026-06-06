"""Application middleware registration helpers."""

from __future__ import annotations

from time import perf_counter

from fastapi import FastAPI, Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from app.utils.metrics import runtime_metrics


def register_metrics_middleware(app: FastAPI) -> None:
    """Register request counting and latency header middleware."""

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = perf_counter()
        runtime_metrics.increment_request(request.url.path)
        response = await call_next(request)
        response.headers["X-Process-Time-ms"] = str(round((perf_counter() - start) * 1000.0, 3))
        return response
