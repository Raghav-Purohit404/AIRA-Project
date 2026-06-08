"""Focused tests for local LLM pipeline helpers."""

from __future__ import annotations

import pytest
import requests

from app.services.llm_local.fallback import recover_json, regex_skill_extraction
from app.services.llm_local.hallucination_guard import HallucinationGuard
from app.services.llm_local.llm_scorer import LLMScorer
from app.services.llm_local.llm_service import LLMServiceError, OllamaLLMService
from app.services.llm_local.skill_extractor import extract_skill_groups


class FakeResponse:
    """Minimal response object for exercising the Ollama client."""

    def __init__(self, payload: dict[str, object], status_error: Exception | None = None) -> None:
        self.payload = payload
        self.status_error = status_error

    def raise_for_status(self) -> None:
        if self.status_error:
            raise self.status_error

    def json(self) -> dict[str, object]:
        return self.payload


class FakeSession:
    """Configurable fake requests session."""

    def __init__(
        self,
        *,
        post_response: FakeResponse | Exception | None = None,
        get_response: FakeResponse | Exception | None = None,
    ) -> None:
        self.post_response = post_response or FakeResponse({"response": "AIRA_OK"})
        self.get_response = get_response or FakeResponse({"models": [{"name": "phi3:3.8b"}]})

    def post(self, *_args: object, **_kwargs: object) -> FakeResponse:
        if isinstance(self.post_response, Exception):
            raise self.post_response
        return self.post_response

    def get(self, *_args: object, **_kwargs: object) -> FakeResponse:
        if isinstance(self.get_response, Exception):
            raise self.get_response
        return self.get_response


def test_ollama_service_generates_text_from_mocked_session() -> None:
    """The Ollama client should parse normal text responses without live Ollama."""
    service = OllamaLLMService(session=FakeSession(), retries=0)

    assert service.generate("health check") == "AIRA_OK"


def test_ollama_service_parses_structured_json() -> None:
    """Structured mode should recover JSON from model text wrappers."""
    session = FakeSession(post_response=FakeResponse({"response": 'Here is JSON: {"score": 91}'}))
    service = OllamaLLMService(session=session, retries=0)

    assert service.generate("score", structured=True) == {"score": 91}


def test_ollama_service_reports_availability_and_missing_model() -> None:
    """Model discovery should distinguish a live API from a missing model."""
    session = FakeSession(get_response=FakeResponse({"models": [{"name": "llama3.2"}]}))
    service = OllamaLLMService(session=session, model="phi3:3.8b")

    assert service.is_available()
    assert service.has_model("llama3.2")
    assert not service.has_model("phi3:3.8b")


def test_ollama_service_wraps_request_failures() -> None:
    """HTTP errors should be surfaced as LLMServiceError with context."""
    service = OllamaLLMService(
        session=FakeSession(post_response=requests.Timeout("timed out")),
        retries=0,
    )

    with pytest.raises(LLMServiceError, match="timed out"):
        service.generate("health check")


def test_skill_extraction_falls_back_when_llm_fails() -> None:
    """Skill extraction should remain useful when Ollama generation fails."""
    service = OllamaLLMService(
        session=FakeSession(post_response=requests.ConnectionError("offline")),
        retries=0,
    )

    groups = extract_skill_groups("Built Python FastAPI services with Docker.", service=service)

    assert "Python" in groups["programming_languages"]
    assert "FastAPI" in groups["frameworks"]
    assert "Docker" in groups["tools"]


def test_json_recovery_handles_fenced_and_embedded_payloads() -> None:
    """Recovery should handle common local-model JSON formatting quirks."""
    assert recover_json('```json\n{"skills": ["Python"]}\n```') == {"skills": ["Python"]}
    assert recover_json('Result follows: [{"skill": "SQL"}]') == [{"skill": "SQL"}]


def test_regex_extraction_and_scoring_pipeline() -> None:
    """Fallback extraction can feed deterministic LLM scoring."""
    groups = regex_skill_extraction("Python, SQL, FastAPI and Redis")
    skills = [(skill, 0.8) for skill in groups["technical_skills"]]

    scored = LLMScorer().score_many(skills, required_skills=["Python", "FastAPI"])

    assert scored[0]["weighted_score"] >= scored[-1]["weighted_score"]
    assert {item["skill"] for item in scored} >= {"Python", "FastAPI", "SQL"}


def test_hallucination_guard_flags_unsupported_terms() -> None:
    """Generated claims should be checked against source context."""
    result = HallucinationGuard().validate(
        "The student knows Python, FastAPI, and Kubernetes.",
        "The student knows Python and FastAPI.",
    )

    assert result.supported is False
    assert "kubernetes" in result.unsupported_terms
