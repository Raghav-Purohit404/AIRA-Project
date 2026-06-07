"""JSON formatting utilities for raw local LLM output."""

from __future__ import annotations

import json
from typing import Any

from app.services.llm_local.fallback import recover_json


class JSONFormatter:
    """Convert raw LLM text into JSON-compatible Python values."""

    def parse(self, text: str) -> dict[str, Any] | list[Any]:
        """Parse raw text and raise a clear error when JSON cannot be recovered."""
        parsed = recover_json(text)
        if not isinstance(parsed, (dict, list)):
            raise ValueError("Unable to recover a JSON object or array from LLM output.")
        return parsed

    def format(self, value: dict[str, Any] | list[Any]) -> str:
        """Return stable, compact JSON for downstream processing."""
        return json.dumps(value, ensure_ascii=False, sort_keys=True)


json_formatter = JSONFormatter()
