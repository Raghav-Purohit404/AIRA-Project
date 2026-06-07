"""Pipeline execution tracing utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class TraceStep:
    """A single pipeline trace step."""

    name: str
    status: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineTrace:
    """Trace state for one pipeline execution."""

    trace_id: str
    pipeline_name: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    steps: list[TraceStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable trace."""
        return {
            "trace_id": self.trace_id,
            "pipeline_name": self.pipeline_name,
            "started_at": self.started_at,
            "steps": [step.__dict__ for step in self.steps],
            "failed": any(step.status == "failed" for step in self.steps),
        }


class PipelineTracer:
    """Capture execution flow and failures for debugging."""

    def start(self, pipeline_name: str) -> PipelineTrace:
        """Create a new trace."""
        return PipelineTrace(trace_id=str(uuid4()), pipeline_name=pipeline_name)

    def add_step(self, trace: PipelineTrace, name: str, status: str = "completed", **details: Any) -> PipelineTrace:
        """Append a step to an existing trace."""
        trace.steps.append(TraceStep(name=name, status=status, details=details))
        return trace

    def capture_failure(self, trace: PipelineTrace, name: str, error: Exception) -> PipelineTrace:
        """Append a failure step with exception details."""
        return self.add_step(trace, name, "failed", error_type=type(error).__name__, message=str(error))


pipeline_tracer = PipelineTracer()
