"""Embedding provider abstractions for local/offline operation."""

from __future__ import annotations

from collections.abc import Protocol, Sequence

from app.services.similarity.similarity_service import SimilarityService


class EmbeddingProvider(Protocol):
    """Protocol implemented by embedding providers."""

    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for text."""


class LocalHashEmbedder:
    """Deterministic offline embedder backed by SimilarityService."""

    def __init__(self, similarity_service: SimilarityService | None = None) -> None:
        self.similarity_service = similarity_service or SimilarityService()

    def embed(self, text: str) -> list[float]:
        """Return a deterministic local embedding."""
        return self.similarity_service.generate_embedding(text)

    def embed_many(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed many texts in input order."""
        return [self.embed(text) for text in texts]


local_hash_embedder = LocalHashEmbedder()
