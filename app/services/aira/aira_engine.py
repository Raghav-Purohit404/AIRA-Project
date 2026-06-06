"""AIRA core scoring engine."""

from __future__ import annotations

from app.models.aira_score import AIRAScore, AIRAScoreBreakdown
from app.models.student_profile import StudentProfile
from app.services.aira.rule_engine import CandidateProfile, RuleEngine
from app.services.aira.weight_config import DEFAULT_WEIGHTS, ScoreWeights


class AIRAEngine:
    """Generate deterministic employability scores from student profiles."""

    def __init__(self, weights: ScoreWeights = DEFAULT_WEIGHTS) -> None:
        self.rule_engine = RuleEngine(weights)

    def score_profile(
        self,
        profile: StudentProfile,
        required_skills: list[str] | None = None,
        ats_weight: float = 0.0,
    ) -> AIRAScore:
        """Score a student profile and return a full AIRA score record."""
        candidate = CandidateProfile(
            cgpa=profile.academic.cgpa,
            skills=profile.skill_names(),
            projects=len(profile.projects),
            internships=len(profile.internships),
            hackathons=len(profile.hackathons),
            achievements=len(profile.achievements),
        )
        result = self.rule_engine.score(candidate, required_skills)
        final_score = self._apply_future_ats_weight(result.total_score, ats_weight)
        breakdown = AIRAScoreBreakdown(
            cgpa_score=result.components["cgpa"],
            skill_score=result.components["skills"],
            project_score=result.components["projects"],
            internship_score=result.components["internships"],
            hackathon_score=result.components["hackathons"],
            achievement_score=result.components["achievements"],
            final_score=final_score,
        )
        return AIRAScore(
            student_id=profile.id,
            breakdown=breakdown,
            normalized_inputs=result.normalized_inputs,
            readiness_level=self.readiness_level(final_score),
        )

    def readiness_level(self, score: float) -> str:
        """Return a placement-readiness label for a score."""
        if score >= 85:
            return "excellent"
        if score >= 70:
            return "strong"
        if score >= 55:
            return "developing"
        return "needs_improvement"

    @staticmethod
    def _apply_future_ats_weight(base_score: float, ats_weight: float) -> float:
        """Reserve a deterministic hook for future ATS score weighting."""
        bounded_weight = max(0.0, min(1.0, ats_weight))
        return round(base_score * (1.0 - bounded_weight), 2)


aira_engine = AIRAEngine()
