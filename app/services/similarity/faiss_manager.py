"""FAISS index manager with an in-memory fallback."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.services.similarity.embedding_metrics import cosine_similarity, normalize_vector

logger = logging.getLogger(__name__)

try:
    import faiss  # type: ignore[import-not-found]
except ImportError:
    faiss = None  # type: ignore[assignment]


class FAISSManager:
    """Create, persist, and search vector indices."""

    def __init__(self, dimension: int, index_path: str | Path | None = None) -> None:
        self.dimension = dimension
        self.index_path = Path(index_path) if index_path else None
        self._metadata: list[dict[str, Any]] = []
        self._fallback_vectors: list[list[float]] = []
        self._index = self._create_index()

    @property
    def using_faiss(self) -> bool:
        """Return whether the native FAISS backend is active."""
        return faiss is not None and self._index is not None

    def add(self, vectors: list[list[float]], metadata: list[dict[str, Any]] | None = None) -> None:
        """Add vectors and optional metadata to the index."""
        normalized = [normalize_vector(vector) for vector in vectors]
        for vector in normalized:
            if len(vector) != self.dimension:
                raise ValueError("Vector dimension does not match index dimension.")
        self._metadata.extend(metadata or [{} for _ in normalized])
        if self.using_faiss:
            import numpy as np

            self._index.add(np.array(normalized, dtype="float32"))  # type: ignore[union-attr]
        else:
            self._fallback_vectors.extend(normalized)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """Search the index and return scored metadata records."""
        query = normalize_vector(query_vector)
        if len(query) != self.dimension:
            raise ValueError("Query vector dimension does not match index dimension.")
        limit = max(1, top_k)
        if self.using_faiss:
            import numpy as np

            scores, indices = self._index.search(np.array([query], dtype="float32"), limit)  # type: ignore[union-attr]
            return [self._result(int(index), float(score)) for score, index in zip(scores[0], indices[0]) if index >= 0]
        scored = [
            self._result(index, cosine_similarity(query, vector))
            for index, vector in enumerate(self._fallback_vectors)
        ]
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]

    def save(self, metadata_path: str | Path | None = None) -> None:
        """Persist the FAISS index and metadata when paths are configured."""
        if self.index_path and self.using_faiss:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self._index, str(self.index_path))  # type: ignore[union-attr]
        if metadata_path:
            path = Path(metadata_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self._metadata, indent=2), encoding="utf-8")

    def load(self, metadata_path: str | Path | None = None) -> None:
        """Load a FAISS index and metadata from disk when available."""
        if self.index_path and self.index_path.exists() and faiss is not None:
            self._index = faiss.read_index(str(self.index_path))
        if metadata_path and Path(metadata_path).exists():
            self._metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))

    def _create_index(self) -> Any | None:
        """Create a cosine-compatible FAISS index when available."""
        if faiss is None:
            logger.info("FAISS is not installed; using in-memory vector fallback.")
            return None
        return faiss.IndexFlatIP(self.dimension)

    def _result(self, index: int, score: float) -> dict[str, Any]:
        """Build a search result from an index position."""
        metadata = self._metadata[index] if index < len(self._metadata) else {}
        return {"index": index, "score": round(float(score), 4), "metadata": metadata}
