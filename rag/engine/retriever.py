"""Vector retrieval abstraction with an in-memory implementation."""

from __future__ import annotations

from typing import Any

from app.services.similarity.similarity_service import SimilarityService, similarity_service
from rag.engine.vector_pipeline import VectorRecord


class VectorRetriever:
    """Retrieve Top-K vector records by cosine similarity."""

    def __init__(
        self,
        records: list[VectorRecord] | None = None,
        similarity: SimilarityService = similarity_service,
    ) -> None:
        self.records = list(records or [])
        self.similarity = similarity

    def add(self, records: list[VectorRecord]) -> None:
        """Add or replace records by identifier."""
        merged = {record.id: record for record in self.records}
        merged.update({record.id: record for record in records})
        self.records = list(merged.values())

    def retrieve(self, query: str, top_k: int = 5, minimum_score: float = -1.0) -> list[dict[str, Any]]:
        """Return the highest-scoring records for a query."""
        query_vector = self.similarity.generate_embedding(query)
        results = []
        for record in self.records:
            score = self.similarity.cosine_similarity(query_vector, record.vector)
            if score >= minimum_score:
                results.append(
                    {
                        "id": record.id,
                        "text": record.text,
                        "metadata": dict(record.metadata),
                        "retrieval_score": round(score, 4),
                    }
                )
        return sorted(results, key=lambda item: (-item["retrieval_score"], item["id"]))[: max(0, top_k)]
