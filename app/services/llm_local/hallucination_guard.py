"""Grounding guard for local LLM outputs."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field


class GroundingResult(BaseModel):
    """Result of validating an LLM output against source context."""

    supported: bool
    confidence: float = Field(ge=0.0, le=1.0)
    unsupported_terms: list[str] = Field(default_factory=list)


class HallucinationGuard:
    """Validate generated text using lexical grounding against source context."""

    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "for",
        "in",
        "is",
        "of",
        "on",
        "the",
        "to",
        "with",
    }

    def validate(self, output: str, source_context: str) -> GroundingResult:
        """Return grounding confidence for generated output."""
        output_terms = self._terms(output)
        context_terms = self._terms(source_context)
        if not output_terms:
            return GroundingResult(supported=True, confidence=1.0)
        unsupported = sorted(output_terms - context_terms)
        confidence = round(1.0 - (len(unsupported) / len(output_terms)), 4)
        return GroundingResult(supported=not unsupported, confidence=max(0.0, confidence), unsupported_terms=unsupported)

    def _terms(self, text: str) -> set[str]:
        """Extract normalized content terms."""
        return {
            token.rstrip(".")
            for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]{1,}", text.casefold())
            if token.rstrip(".") not in self.STOPWORDS
        }


hallucination_guard = HallucinationGuard()
