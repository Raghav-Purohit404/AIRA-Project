"""Token-aware semantic document chunking."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DocumentChunk:
    """A retrieval-ready document segment."""

    id: str
    text: str
    metadata: dict[str, Any]
    token_count: int


class SemanticChunker:
    """Group paragraph and sentence units within token budgets."""

    def __init__(self, max_tokens: int = 220, overlap_tokens: int = 30) -> None:
        if max_tokens < 10 or overlap_tokens < 0 or overlap_tokens >= max_tokens:
            raise ValueError("Chunk token limits are invalid.")
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def chunk(
        self,
        text: str,
        document_id: str = "document",
        metadata: dict[str, Any] | None = None,
    ) -> list[DocumentChunk]:
        """Split text while preferring paragraph and sentence boundaries."""
        units = [
            unit.strip()
            for paragraph in re.split(r"\n\s*\n", text)
            for unit in re.split(r"(?<=[.!?])\s+", paragraph.strip())
            if unit.strip()
        ]
        chunks: list[DocumentChunk] = []
        current: list[str] = []
        for unit in units:
            words = unit.split()
            if len(words) > self.max_tokens:
                if current:
                    chunks.append(self._build(document_id, len(chunks), current, metadata))
                    current = []
                for start in range(0, len(words), self.max_tokens - self.overlap_tokens):
                    window = words[start : start + self.max_tokens]
                    chunks.append(self._build(document_id, len(chunks), window, metadata))
                    if start + self.max_tokens >= len(words):
                        break
                continue
            if current and len(current) + len(words) > self.max_tokens:
                chunks.append(self._build(document_id, len(chunks), current, metadata))
                current = current[-self.overlap_tokens :] if self.overlap_tokens else []
            current.extend(words)
        if current:
            chunks.append(self._build(document_id, len(chunks), current, metadata))
        return chunks

    @staticmethod
    def _build(
        document_id: str,
        index: int,
        words: list[str],
        metadata: dict[str, Any] | None,
    ) -> DocumentChunk:
        """Build a chunk with stable identity and inherited metadata."""
        chunk_metadata = dict(metadata or {})
        chunk_metadata.update({"document_id": document_id, "chunk_index": index})
        return DocumentChunk(
            id=f"{document_id}:{index}",
            text=" ".join(words),
            metadata=chunk_metadata,
            token_count=len(words),
        )
