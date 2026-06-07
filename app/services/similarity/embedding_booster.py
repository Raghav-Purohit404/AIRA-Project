"""Embedding weighting strategies for recruitment-critical terms."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence


class EmbeddingBooster:
    """Apply deterministic vector boosts for critical skills."""

    def boost(
        self,
        vector: Sequence[float],
        text: str,
        critical_skills: list[str],
        *,
        weight: float = 0.15,
    ) -> list[float]:
        """Return a normalized vector with critical-skill dimensions emphasized."""
        boosted = [float(value) for value in vector]
        if not boosted:
            return boosted
        lower_text = text.casefold()
        for skill in critical_skills:
            if skill.casefold() not in lower_text:
                continue
            index = self._index(skill, len(boosted))
            boosted[index] += weight
        magnitude = math.sqrt(sum(value * value for value in boosted))
        return [value / magnitude for value in boosted] if magnitude else boosted

    def _index(self, skill: str, dimensions: int) -> int:
        """Map a skill to a stable vector dimension."""
        digest = hashlib.blake2b(skill.casefold().encode("utf-8"), digest_size=4).digest()
        return int.from_bytes(digest, "big") % dimensions


embedding_booster = EmbeddingBooster()
