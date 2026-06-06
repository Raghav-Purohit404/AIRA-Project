"""Document preprocessing and RAG ingestion orchestration."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rag.engine.chunker import DocumentChunk, SemanticChunker
from rag.engine.vector_pipeline import VectorPipeline, VectorRecord


class DocumentIngestion:
    """Convert documents into retrieval-ready vector records."""

    def __init__(
        self,
        chunker: SemanticChunker | None = None,
        vector_pipeline: VectorPipeline | None = None,
    ) -> None:
        self.chunker = chunker or SemanticChunker()
        self.vector_pipeline = vector_pipeline or VectorPipeline()

    def ingest_text(
        self,
        text: str,
        source: str = "inline",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, object]:
        """Preprocess, chunk, and embed a document."""
        cleaned = self.preprocess(text)
        if not cleaned:
            raise ValueError("Document contains no ingestible text.")
        document_id = hashlib.sha256(f"{source}:{cleaned}".encode("utf-8")).hexdigest()[:20]
        extracted = {
            "source": source,
            "document_id": document_id,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
            "character_count": len(cleaned),
            **(metadata or {}),
        }
        chunks: list[DocumentChunk] = self.chunker.chunk(cleaned, document_id, extracted)
        records: list[VectorRecord] = self.vector_pipeline.prepare(chunks)
        return {"document_id": document_id, "metadata": extracted, "chunks": chunks, "records": records}

    def ingest_file(self, path: str | Path, metadata: dict[str, Any] | None = None) -> dict[str, object]:
        """Ingest a UTF-8 text-compatible file."""
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        return self.ingest_text(
            text,
            source=str(file_path),
            metadata={"filename": file_path.name, "extension": file_path.suffix, **(metadata or {})},
        )

    @staticmethod
    def preprocess(text: str) -> str:
        """Normalize control characters and excessive whitespace."""
        printable = "".join(char if char.isprintable() or char in "\n\t" else " " for char in text)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in printable.splitlines()]
        return "\n".join(line for line in lines if line).strip()


document_ingestion = DocumentIngestion()
