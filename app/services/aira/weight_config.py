"""Weight configuration for deterministic AIRA rule scoring."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreWeights:
    """Maximum contribution of each scoring component."""

    cgpa: float = 30.0
    skills: float = 25.0
    projects: float = 15.0
    internships: float = 15.0
    hackathons: float = 10.0
    achievements: float = 5.0

    @property
    def total(self) -> float:
        """Return the sum of all score weights."""
        return self.cgpa + self.skills + self.projects + self.internships + self.hackathons + self.achievements


DEFAULT_WEIGHTS = ScoreWeights()


def get_default_weights() -> ScoreWeights:
    """Return the default AIRA scoring weights."""
    return DEFAULT_WEIGHTS
