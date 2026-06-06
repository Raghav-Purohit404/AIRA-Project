"""Lightweight periodic and cron-style job scheduler."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

JobCallable = Callable[[], Any]


@dataclass
class ScheduledJob:
    """Job definition and execution state."""

    name: str
    callback: JobCallable
    next_run: datetime
    interval: timedelta | None = None
    cron: str | None = None
    last_run: datetime | None = None
    run_count: int = 0
    last_error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class JobScheduler:
    """Execute due jobs with interval or five-field cron schedules."""

    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}

    def add_interval_job(
        self,
        name: str,
        callback: JobCallable,
        seconds: float,
        run_immediately: bool = False,
    ) -> ScheduledJob:
        """Register a fixed-interval job."""
        if seconds <= 0:
            raise ValueError("Job interval must be positive.")
        now = datetime.now(timezone.utc)
        job = ScheduledJob(
            name=name,
            callback=callback,
            interval=timedelta(seconds=seconds),
            next_run=now if run_immediately else now + timedelta(seconds=seconds),
        )
        self._jobs[name] = job
        return job

    def add_cron_job(self, name: str, callback: JobCallable, expression: str) -> ScheduledJob:
        """Register a UTC five-field cron job."""
        self._validate_cron(expression)
        job = ScheduledJob(
            name=name,
            callback=callback,
            cron=expression,
            next_run=self._next_cron(expression, datetime.now(timezone.utc)),
        )
        self._jobs[name] = job
        return job

    async def run_pending(self, now: datetime | None = None) -> list[dict[str, Any]]:
        """Execute every due job and return structured outcomes."""
        current = now or datetime.now(timezone.utc)
        outcomes: list[dict[str, Any]] = []
        for job in list(self._jobs.values()):
            if job.next_run > current:
                continue
            try:
                result = job.callback()
                if inspect.isawaitable(result):
                    result = await result
                job.last_error = None
                outcomes.append({"name": job.name, "success": True, "result": result})
            except Exception as exc:
                job.last_error = str(exc)
                outcomes.append({"name": job.name, "success": False, "error": str(exc)})
            finally:
                job.last_run = current
                job.run_count += 1
                job.next_run = (
                    current + job.interval
                    if job.interval is not None
                    else self._next_cron(str(job.cron), current)
                )
        return outcomes

    async def serve(self, poll_seconds: float = 1.0, stop_event: asyncio.Event | None = None) -> None:
        """Run the scheduler until the optional stop event is set."""
        event = stop_event or asyncio.Event()
        while not event.is_set():
            await self.run_pending()
            try:
                await asyncio.wait_for(event.wait(), timeout=poll_seconds)
            except TimeoutError:
                continue

    def remove(self, name: str) -> bool:
        """Remove a scheduled job."""
        return self._jobs.pop(name, None) is not None

    def jobs(self) -> tuple[ScheduledJob, ...]:
        """Return current job definitions."""
        return tuple(self._jobs.values())

    @staticmethod
    def _validate_cron(expression: str) -> None:
        """Validate supported five-field cron syntax."""
        fields = expression.split()
        if len(fields) != 5:
            raise ValueError("Cron expression must have five fields.")
        limits = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 6))
        for field, (minimum, maximum) in zip(fields, limits):
            if field == "*":
                continue
            if not field.isdigit() or not minimum <= int(field) <= maximum:
                raise ValueError(f"Unsupported cron field: {field}")

    @classmethod
    def _next_cron(cls, expression: str, after: datetime) -> datetime:
        """Find the next matching UTC minute for simple cron fields."""
        cls._validate_cron(expression)
        fields = expression.split()
        candidate = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(366 * 24 * 60):
            values = (candidate.minute, candidate.hour, candidate.day, candidate.month, candidate.weekday())
            if all(field == "*" or int(field) == value for field, value in zip(fields, values)):
                return candidate
            candidate += timedelta(minutes=1)
        raise ValueError("Cron expression did not match within one year.")


scheduler = JobScheduler()
