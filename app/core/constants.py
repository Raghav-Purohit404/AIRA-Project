"""Central application constants for AIRA."""

from __future__ import annotations

from enum import StrEnum


class UserRole(str, StrEnum):
    """Supported authorization roles."""

    ADMIN = "admin"
    FACULTY = "faculty"
    STUDENT = "student"
    RECRUITER = "recruiter"


class ResumeTemplate(str, StrEnum):
    """Supported resume template identifiers."""

    ATS = "ats"
    MODERN = "modern"
    ACADEMIC = "academic"


APP_NAME = "AIRA"
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

SUPPORTED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
SUPPORTED_DATA_EXTENSIONS = {".csv", ".json", ".jsonl", ".xlsx"}
SUPPORTED_DOCUMENT_EXTENSIONS = SUPPORTED_RESUME_EXTENSIONS | SUPPORTED_DATA_EXTENSIONS

DEFAULT_SCORING_WEIGHTS: dict[str, float] = {
    "cgpa": 0.25,
    "skills": 0.30,
    "projects": 0.15,
    "internships": 0.15,
    "hackathons": 0.05,
    "achievements": 0.10,
}

BENCHMARK_THRESHOLDS: dict[str, float] = {
    "minimum_accuracy": 0.80,
    "minimum_retrieval_mrr": 0.50,
    "maximum_latency_ms": 1000.0,
    "maximum_embedding_latency_ms": 250.0,
    "maximum_score_drift": 2.5,
}

CANONICAL_SKILL_ALIASES: dict[str, str] = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "dbms": "Database Management Systems",
    "sql": "SQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "fast api": "FastAPI",
    "fastapi": "FastAPI",
}
