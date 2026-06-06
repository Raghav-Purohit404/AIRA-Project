"""Dependency-aware AIRA rescoring orchestration."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.models.aira_score import AIRAScore
from app.models.student_profile import StudentProfile
from app.services.aira.aira_engine import AIRAEngine, aira_engine

PipelineHook = Callable[[str, dict[str, Any]], None]


@dataclass(frozen=True)
class RescoringResult:
    """Outcome of one incremental rescoring operation."""

    profile_id: str
    invalidated: tuple[str, ...]
    score: AIRAScore | None
    skipped: bool
    rescored_at: str


class RescoringService:
    """Invalidate affected outputs and re-trigger dependent pipelines."""

    dependency_map = {
        "skills": ("embedding", "similarity", "aira_score", "ranking"),
        "projects": ("embedding", "similarity", "aira_score", "ranking"),
        "internships": ("embedding", "similarity", "aira_score", "ranking"),
        "cgpa": ("aira_score", "ranking"),
    }

    def __init__(self, engine: AIRAEngine = aira_engine) -> None:
        self.engine = engine
        self._scores: dict[str, AIRAScore] = {}
        self._hooks: list[PipelineHook] = []

    def register_hook(self, hook: PipelineHook) -> None:
        """Register a pipeline refresh hook."""
        self._hooks.append(hook)

    def affected_dependencies(self, changed_fields: Iterable[str]) -> tuple[str, ...]:
        """Resolve an ordered set of downstream invalidations."""
        ordered = ("embedding", "similarity", "aira_score", "ranking")
        affected = {item for field in changed_fields for item in self.dependency_map.get(field, ())}
        return tuple(item for item in ordered if item in affected)

    def rescore(
        self,
        profile: StudentProfile,
        changed_fields: Iterable[str],
        required_skills: list[str] | None = None,
        force: bool = False,
    ) -> RescoringResult:
        """Perform incremental rescoring and publish dependency refresh events."""
        invalidated = self.affected_dependencies(changed_fields)
        if not invalidated and not force:
            return RescoringResult(
                profile_id=profile.id,
                invalidated=(),
                score=self._scores.get(profile.id),
                skipped=True,
                rescored_at=datetime.now(timezone.utc).isoformat(),
            )
        score = self.engine.score_profile(profile, required_skills)
        self._scores[profile.id] = score
        context = {"profile": profile, "score": score, "invalidated": invalidated}
        for dependency in invalidated or ("aira_score", "ranking"):
            for hook in tuple(self._hooks):
                hook(dependency, context)
        return RescoringResult(
            profile_id=profile.id,
            invalidated=invalidated,
            score=score,
            skipped=False,
            rescored_at=datetime.now(timezone.utc).isoformat(),
        )

    def invalidate(self, profile_id: str) -> bool:
        """Invalidate a cached score."""
        return self._scores.pop(profile_id, None) is not None

    def batch_rescore(
        self,
        profiles: Iterable[StudentProfile],
        required_skills: list[str] | None = None,
    ) -> list[RescoringResult]:
        """Force a full score and ranking refresh for a profile batch."""
        return [self.rescore(profile, self.dependency_map, required_skills, force=True) for profile in profiles]


rescoring_service = RescoringService()
