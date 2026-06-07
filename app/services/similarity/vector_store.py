"""Metadata-aware vector storage abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.services.similarity.embedder import LocalHashEmbedder
from app.services.similarity.faiss_manager import FAISSManager


@dataclass
class VectorDocument:
    """A stored vector document."""

    id: str
    text: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore:
    """Store text, vectors, and metadata behind a FAISS-compatible manager."""

    def __init__(
        self,
        dimension: int = 256,
        embedder: LocalHashEmbedder | None = None,
        manager: FAISSManager | None = None,
    ) -> None:
        self.embedder = embedder or LocalHashEmbedder()
        self.manager = manager or FAISSManager(dimension)
        self.documents: list[VectorDocument] = []

    def add_texts(self, texts: list[str], metadatas: list[dict[str, Any]] | None = None) -> list[str]:
        """Embed and store texts with metadata."""
        metadatas = metadatas or [{} for _ in texts]
        documents: list[VectorDocument] = []
        for index, text in enumerate(texts):
            document_id = str(metadatas[index].get("id", f"doc-{len(self.documents) + index + 1}"))
            documents.append(
                VectorDocument(
                    id=document_id,
                    text=text,
                    vector=self.embedder.embed(text),
                    metadata=metadatas[index],
                )
            )
        self.documents.extend(documents)
        self.manager.add(
            [document.vector for document in documents],
            [{"id": document.id, "text": document.text, **document.metadata} for document in documents],
        )
        return [document.id for document in documents]

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Search stored documents by query text."""
        query_vector = self.embedder.embed(query)
        return self.manager.search(query_vector, top_k=top_k)


vector_store = VectorStore()
