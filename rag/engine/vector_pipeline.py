"""Embedding and vector-index preparation without a concrete index backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.similarity.similarity_service import SimilarityService, similarity_service
from rag.engine.chunker import DocumentChunk


@dataclass(frozen=True)
class VectorRecord:
    """A vector plus source text and metadata ready for indexing."""

    id: str
    vector: list[float]
    text: str
    metadata: dict[str, Any]


class VectorPipeline:
    """Prepare chunk vectors for in-memory or future FAISS indexes."""

    def __init__(self, similarity: SimilarityService = similarity_service) -> None:
        self.similarity = similarity

    def prepare(self, chunks: list[DocumentChunk]) -> list[VectorRecord]:
        """Embed chunks and return index-neutral records."""
        return [
            VectorRecord(
                id=chunk.id,
                vector=self.similarity.generate_embedding(chunk.text),
                text=chunk.text,
                metadata=dict(chunk.metadata),
            )
            for chunk in chunks
        ]

    def index_payload(self, records: list[VectorRecord]) -> dict[str, object]:
        """Return arrays suitable for a future vector database adapter."""
        dimensions = len(records[0].vector) if records else 0
        return {
            "ids": [record.id for record in records],
            "vectors": [record.vector for record in records],
            "metadata": [record.metadata for record in records],
            "dimensions": dimensions,
        }
