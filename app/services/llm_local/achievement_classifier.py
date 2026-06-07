"""Achievement classification helpers."""

from __future__ import annotations

from app.models.achievements import AchievementType


class AchievementClassifier:
    """Classify achievement text into deterministic categories."""

    KEYWORDS: dict[AchievementType, set[str]] = {
        AchievementType.ACADEMIC: {"cgpa", "rank", "topper", "scholarship", "academic", "semester"},
        AchievementType.TECHNICAL: {"project", "hackathon", "coding", "software", "patent", "publication"},
        AchievementType.LEADERSHIP: {"lead", "captain", "coordinator", "president", "secretary", "organizer"},
        AchievementType.CERTIFICATION: {"certified", "certification", "credential", "course"},
    }

    def classify(self, title: str, description: str | None = None) -> AchievementType:
        """Classify an achievement from title and optional description."""
        text = f"{title} {description or ''}".casefold()
        scores = {
            category: sum(1 for keyword in keywords if keyword in text)
            for category, keywords in self.KEYWORDS.items()
        }
        best_category = max(scores, key=scores.get)
        return best_category if scores[best_category] > 0 else AchievementType.OTHER


achievement_classifier = AchievementClassifier()
