"""Resilient client for the local Ollama generation API."""

from __future__ import annotations

import os
from time import sleep
from typing import Any

import requests

from app.services.llm_local.fallback import recover_json


class LLMServiceError(RuntimeError):
    """Raised when Ollama cannot produce a valid response."""


class OllamaLLMService:
    """Call Ollama with configurable retries, timeouts, and JSON parsing."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        retries: int = 2,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "phi3:3.8b")
        self.timeout = timeout or float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "30"))
        self.retries = max(0, retries)
        self.session = session or requests.Session()

    def generate(
        self,
        prompt: str,
        *,
        structured: bool = False,
        model: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> str | dict[str, Any] | list[Any]:
        """Generate text or a parsed JSON response."""
        payload: dict[str, Any] = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": False,
            "options": options or {"temperature": 0.1},
        }
        if structured:
            payload["format"] = "json"
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                text = str(response.json().get("response", "")).strip()
                if not text:
                    raise LLMServiceError("Ollama returned an empty response.")
                if not structured:
                    return text
                parsed = recover_json(text)
                if parsed is None:
                    raise LLMServiceError("Ollama returned malformed JSON.")
                return parsed
            except (requests.RequestException, ValueError, LLMServiceError) as exc:
                last_error = exc
                if attempt < self.retries:
                    sleep(min(0.25 * (2**attempt), 2.0))
        raise LLMServiceError(f"Ollama request failed after {self.retries + 1} attempts.") from last_error


llm_service = OllamaLLMService()


def generate(prompt: str) -> str:
    """Backward-compatible text generation function."""
    result = llm_service.generate(prompt)
    return str(result)
