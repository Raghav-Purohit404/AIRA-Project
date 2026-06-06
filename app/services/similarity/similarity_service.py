"""Embedding abstraction and semantic similarity operations."""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

from app.services.similarity.embedding_cache import EmbeddingCache
from app.services.similarity.profile_to_text import ProfileToTextConverter

EmbeddingProvider = Callable[[str], Sequence[float]]


class SimilarityService:
    """Provide deterministic local similarity with pluggable embeddings."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        cache: EmbeddingCache | None = None,
        dimensions: int = 256,
    ) -> None:
        self.embedding_provider = embedding_provider or self._hashed_embedding
        self.cache = cache or EmbeddingCache()
        self.dimensions = dimensions

    def generate_embedding(self, text: str) -> list[float]:
        """Generate or retrieve a normalized embedding for text."""
        normalized = " ".join(text.split()).casefold()
        cache_key = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        vector = [float(value) for value in self.embedding_provider(normalized)]
        if not vector:
            raise ValueError("Embedding provider returned an empty vector.")
        self.cache.set(cache_key, vector)
        return vector

    def cosine_similarity(self, vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
        """Calculate cosine similarity for equal-length vectors."""
        if len(vector_a) != len(vector_b) or not vector_a:
            raise ValueError("Vectors must be non-empty and have equal dimensions.")
        dot = sum(a * b for a, b in zip(vector_a, vector_b))
        magnitude_a = math.sqrt(sum(value * value for value in vector_a))
        magnitude_b = math.sqrt(sum(value * value for value in vector_b))
        if magnitude_a == 0.0 or magnitude_b == 0.0:
            return 0.0
        return max(-1.0, min(1.0, dot / (magnitude_a * magnitude_b)))

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic text similarity."""
        return round(
            self.cosine_similarity(self.generate_embedding(text1), self.generate_embedding(text2)),
            4,
        )

    def compare_profiles(self, first: Mapping[str, Any] | Any, second: Mapping[str, Any] | Any) -> float:
        """Compare two structured student profiles."""
        return self.calculate_similarity(
            ProfileToTextConverter.convert(first),
            ProfileToTextConverter.convert(second),
        )

    def match_job_description(self, profile: Mapping[str, Any] | Any, job_description: str) -> float:
        """Return profile-to-job-description relevance."""
        return self.calculate_similarity(ProfileToTextConverter.convert(profile), job_description)

    def top_k(
        self,
        query: str,
        documents: Iterable[tuple[str, str] | Mapping[str, Any]],
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve the Top-K documents by cosine similarity."""
        query_vector = self.generate_embedding(query)
        scored: list[dict[str, Any]] = []
        for document in documents:
            if isinstance(document, Mapping):
                identifier = str(document.get("id", ""))
                text = str(document.get("text", ""))
                metadata = dict(document.get("metadata", {}))
            else:
                identifier, text = document
                metadata = {}
            score = self.cosine_similarity(query_vector, self.generate_embedding(text))
            scored.append({"id": identifier, "text": text, "score": round(score, 4), "metadata": metadata})
        return sorted(scored, key=lambda item: (-item["score"], item["id"]))[: max(0, k)]

    def _hashed_embedding(self, text: str) -> list[float]:
        """Create a deterministic token-hashing vector for offline operation."""
        vector = [0.0] * self.dimensions
        for token in re.findall(r"[a-z0-9+#.]+", text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        magnitude = math.sqrt(sum(value * value for value in vector))
        return [value / magnitude for value in vector] if magnitude else vector


similarity_service = SimilarityService()
