"""Weighted retrieval reranking with semantic extension hooks."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

SemanticHook = Callable[[str, dict[str, Any]], float]


class WeightedReranker:
    """Blend retrieval score, metadata signals, and optional semantic scores."""

    def __init__(
        self,
        retrieval_weight: float = 0.75,
        metadata_weight: float = 0.1,
        semantic_weight: float = 0.15,
        semantic_hook: SemanticHook | None = None,
    ) -> None:
        total = retrieval_weight + metadata_weight + semantic_weight
        if total <= 0:
            raise ValueError("At least one reranking weight must be positive.")
        self.retrieval_weight = retrieval_weight / total
        self.metadata_weight = metadata_weight / total
        self.semantic_weight = semantic_weight / total
        self.semantic_hook = semantic_hook

    def rerank(
        self,
        query: str,
        results: list[dict[str, Any]],
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return results ordered by a weighted final score."""
        reranked: list[dict[str, Any]] = []
        for result in results:
            metadata = result.get("metadata", {})
            metadata_score = float(metadata.get("priority", 0.0)) if isinstance(metadata, dict) else 0.0
            semantic_score = self.semantic_hook(query, result) if self.semantic_hook else 0.0
            final_score = (
                float(result.get("retrieval_score", 0.0)) * self.retrieval_weight
                + max(0.0, min(1.0, metadata_score)) * self.metadata_weight
                + max(0.0, min(1.0, semantic_score)) * self.semantic_weight
            )
            reranked.append({**result, "rerank_score": round(final_score, 4)})
        ordered = sorted(reranked, key=lambda item: (-item["rerank_score"], str(item.get("id", ""))))
        return ordered[:top_k] if top_k is not None else ordered
