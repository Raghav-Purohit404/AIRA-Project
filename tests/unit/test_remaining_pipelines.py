"""Focused tests for ranking, ingestion, RAG, cache, and scheduling."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.schemas.faculty_schema import CandidateFilterRequest
from app.services.cache.redis_client import RedisCache
from app.services.ingestion.change_detector import ChangeDetector
from app.services.ranking.ranking_service import RankingService
from app.services.similarity.similarity_service import SimilarityService
from jobs.scheduler import JobScheduler
from rag.engine.chunker import SemanticChunker
from rag.engine.retriever import VectorRetriever
from rag.engine.vector_pipeline import VectorPipeline


def test_ranking_filters_and_breaks_ties() -> None:
    """Ranking should filter skills and use CGPA for equal AIRA scores."""
    candidates = [
        {
            "student_id": "a",
            "name": "A",
            "aira_score": 90,
            "department": "CSE",
            "skills": ["Python"],
            "cgpa": 8.0,
        },
        {
            "student_id": "b",
            "name": "B",
            "aira_score": 90,
            "department": "CSE",
            "skills": ["Python", "FastAPI"],
            "cgpa": 9.0,
        },
    ]
    response = RankingService().rank(
        candidates,
        CandidateFilterRequest(skills=["Python"], minimum_cgpa=8.0),
    )
    assert [candidate.student_id for candidate in response.candidates] == ["b", "a"]
    assert response.metadata.filtered_candidates == 2


def test_change_detector_reports_added_skills() -> None:
    """Change reports should include field details."""
    report = ChangeDetector().detect(
        {"skills": ["Python"], "cgpa": 8.0, "projects": [], "internships": []},
        {"skills": ["Python", "FastAPI"], "cgpa": 8.0, "projects": [], "internships": []},
    )
    assert report["changed_fields"] == ["skills"]
    assert report["changes"][0]["added"] == ["fastapi"]


def test_cache_json_and_delete() -> None:
    """Memory fallback should preserve JSON-compatible values."""
    cache = RedisCache(connect=False)
    assert cache.set("candidate", {"score": 91.2}, ttl=60)
    assert cache.get("candidate") == {"score": 91.2}
    assert cache.delete("candidate")
    assert cache.get("candidate") is None


def test_rag_pipeline_retrieves_relevant_chunk() -> None:
    """Prepared vectors should be retrievable without FAISS."""
    similarity = SimilarityService()
    chunks = SemanticChunker(max_tokens=20, overlap_tokens=2).chunk(
        "Python FastAPI backend development. React frontend interface.",
        "profile",
    )
    records = VectorPipeline(similarity).prepare(chunks)
    results = VectorRetriever(records, similarity).retrieve("Python backend", top_k=1)
    assert results
    assert "Python" in results[0]["text"]


def test_scheduler_executes_due_async_job() -> None:
    """Scheduler should execute and account for due jobs."""
    scheduler = JobScheduler()
    calls: list[str] = []
    scheduler.add_interval_job("sample", lambda: calls.append("ran"), seconds=10, run_immediately=True)
    outcomes = asyncio.run(scheduler.run_pending(datetime.now(timezone.utc)))
    assert outcomes[0]["success"] is True
    assert calls == ["ran"]
