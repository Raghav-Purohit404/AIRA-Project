"""Nightly batch rescoring and ranking refresh job."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from typing import Any

from app.models.student_profile import StudentProfile
from app.services.aira.rescoring_service import RescoringService, rescoring_service

RankingRefreshHook = Callable[[list[str]], Any]


class NightlyRescoringJob:
    """Rescore active profiles and notify ranking refresh adapters."""

    def __init__(
        self,
        profile_provider: Callable[[], Iterable[StudentProfile]],
        rescoring: RescoringService = rescoring_service,
        ranking_refresh: RankingRefreshHook | None = None,
    ) -> None:
        self.profile_provider = profile_provider
        self.rescoring = rescoring
        self.ranking_refresh = ranking_refresh

    def run(self, required_skills: list[str] | None = None) -> dict[str, Any]:
        """Execute one complete nightly rescoring batch."""
        profiles = list(self.profile_provider())
        results = self.rescoring.batch_rescore(profiles, required_skills)
        profile_ids = [result.profile_id for result in results if not result.skipped]
        refresh_result = self.ranking_refresh(profile_ids) if self.ranking_refresh else None
        return {
            "success": True,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "profiles_seen": len(profiles),
            "profiles_rescored": len(profile_ids),
            "profile_ids": profile_ids,
            "ranking_refresh": refresh_result,
        }
