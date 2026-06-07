"""Prompt preprocessing helpers for local LLM calls."""

from __future__ import annotations

import re


class LLMPreprocessor:
    """Clean and normalize prompts before sending them to Ollama."""

    CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

    def clean(self, prompt: str, *, max_chars: int = 12000) -> str:
        """Return a whitespace-normalized prompt with control characters removed."""
        without_controls = self.CONTROL_CHARS.sub(" ", prompt)
        normalized = re.sub(r"\s+", " ", without_controls).strip()
        return normalized[:max_chars]

    def build_instruction(self, system_instruction: str, user_content: str) -> str:
        """Combine system and user text into a compact local-model prompt."""
        return self.clean(f"{system_instruction.strip()}\n\nInput:\n{user_content.strip()}")


llm_preprocessor = LLMPreprocessor()
