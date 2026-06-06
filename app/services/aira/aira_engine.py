<<<<<<< HEAD
"""AIRA core scoring engine."""
=======
from app.utils.validators import Validator

from app.services.aira.normalization import (
    normalize_cgpa,
    normalize_hackathons,
    normalize_internships
)
>>>>>>> f2518c328c9e200c19ddfe1045e3edc568ddae2b

from __future__ import annotations

from app.models.aira_score import AIRAScore, AIRAScoreBreakdown
from app.models.student_profile import StudentProfile
from app.services.aira.rule_engine import CandidateProfile, RuleEngine
from app.services.aira.weight_config import DEFAULT_WEIGHTS, ScoreWeights


<<<<<<< HEAD
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

    def _apply_future_ats_weight(self, base_score: float, ats_weight: float) -> float:
        """Reserve a deterministic hook for future ATS score weighting."""
        bounded_weight = max(0.0, min(1.0, ats_weight))
        return round(base_score * (1.0 - bounded_weight), 2)


aira_engine = AIRAEngine()
=======
def run_aira_engine(profile):

    Validator.validate_cgpa(profile["cgpa"])

    profile["cgpa"] = normalize_cgpa(profile["cgpa"])

    profile["hackathons"] = normalize_hackathons(
        profile["hackathons"]
    )

    profile["internships"] = normalize_internships(
        profile["internships"]
    )

    score = calculate_rule_score(profile)

    explanation = explain_score(
        profile,
        score
    )

    return {
        "aira_score": score,
        "explanation": explanation
    }


if __name__ == "__main__":

    sample_profile = {

        "cgpa": 8.7,

        "skills": [
            "Python",
            "FastAPI",
            "React",
            "SQL"
        ],

        "projects": [
            "AIRA",
            "Resume Analyzer"
        ],

        "internships": 2,

        "hackathons": 3
    }

    result = run_aira_engine(
        sample_profile
    )

    print("\n========== FINAL AIRA RESULT ==========")

    print("\nAIRA SCORE:")
    print(result["aira_score"])

    print("\nEXPLANATION:")

    for line in result["explanation"]:
        print("•", line)
        
>>>>>>> f2518c328c9e200c19ddfe1045e3edc568ddae2b
