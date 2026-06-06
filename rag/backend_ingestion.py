"""Backend-facing wrapper for RAG document and profile ingestion."""

from __future__ import annotations

from typing import Any

from app.services.similarity.profile_to_text import ProfileToTextConverter
from rag.engine.retriever import VectorRetriever
from rag.ingestion import DocumentIngestion, document_ingestion


class BackendIngestionService:
    """Ingest backend entities and update a retrieval adapter."""

    def __init__(
        self,
        ingestion: DocumentIngestion = document_ingestion,
        retriever: VectorRetriever | None = None,
    ) -> None:
        self.ingestion = ingestion
        self.retriever = retriever or VectorRetriever()

    def ingest_document(
        self,
        text: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, object]:
        """Ingest arbitrary backend text and index its vectors."""
        result = self.ingestion.ingest_text(text, source, metadata)
        self.retriever.add(result["records"])
        return {
            "document_id": result["document_id"],
            "chunk_count": len(result["chunks"]),
            "metadata": result["metadata"],
        }

    def ingest_profile(self, profile: dict[str, Any] | Any) -> dict[str, object]:
        """Convert and ingest a student profile."""
        data = profile.model_dump(mode="json") if hasattr(profile, "model_dump") else dict(profile)
        profile_id = str(data.get("id") or data.get("student_id") or "")
        if not profile_id:
            raise ValueError("Profile identifier is required.")
        return self.ingest_document(
            ProfileToTextConverter.convert(data),
            source=f"profile:{profile_id}",
            metadata={"entity_type": "student_profile", "profile_id": profile_id},
        )


backend_ingestion_service = BackendIngestionService()
