"""Deterministic seed data for local development and future persistence."""

from __future__ import annotations

from datetime import date
from typing import Any


def seed_students() -> list[dict[str, Any]]:
    """Return representative student profiles for local demos."""
    return [
        {
            "basic_info": {
                "full_name": "Ananya Rao",
                "email": "ananya.rao@example.edu",
                "department": "Computer Science",
                "batch_year": 2026,
            },
            "academic": {
                "degree": "B.Tech",
                "department": "Computer Science",
                "graduation_year": 2026,
                "cgpa": 8.8,
                "semesters": [{"semester": 1, "sgpa": 8.4, "credits": 22}],
            },
            "skills": [{"name": "Python", "level": "advanced"}, {"name": "FastAPI", "level": "intermediate"}],
            "projects": [{"title": "Recruitment Analytics", "description": "Ranking dashboard for students.", "technologies": ["Python", "SQL"]}],
            "internships": [{"company": "Acme AI", "role": "Backend Intern", "start_date": "2025-05-01"}],
            "hackathons": [{"name": "Smart India Hackathon"}],
            "achievements": [{"title": "Department Topper", "category": "academic"}],
        }
    ]


def seed_faculty() -> list[dict[str, str]]:
    """Return representative faculty users."""
    return [
        {"full_name": "Dr. Meera Nair", "email": "meera.nair@example.edu", "department": "Computer Science"},
        {"full_name": "Prof. Arjun Sen", "email": "arjun.sen@example.edu", "department": "Information Technology"},
    ]


def seed_job_descriptions() -> list[dict[str, Any]]:
    """Return local job descriptions for ranking and matching demos."""
    return [
        {
            "role_title": "Backend Engineering Intern",
            "required_skills": ["Python", "FastAPI", "SQL"],
            "preferred_skills": ["Docker", "Redis"],
            "education_requirements": ["B.Tech Computer Science or related branch"],
            "experience_requirements": ["Prior internship or project experience preferred"],
            "extracted_keywords": ["api", "backend", "database", "testing"],
        }
    ]


def seed_benchmark_dataset() -> dict[str, Any]:
    """Return benchmark fixtures for extraction, ranking, and scoring checks."""
    return {
        "generated_on": date.today().isoformat(),
        "skill_extraction": [
            {"text": "Python FastAPI SQL backend internship.", "expected": ["Python", "FastAPI", "SQL"]}
        ],
        "retrieval": [
            {"query": "backend python", "relevant_id": "profile-1", "documents": [{"id": "profile-1", "text": "Python backend API"}]}
        ],
    }


def build_seed_payload() -> dict[str, Any]:
    """Return all seed data grouped by target domain."""
    return {
        "students": seed_students(),
        "faculty": seed_faculty(),
        "job_descriptions": seed_job_descriptions(),
        "benchmarks": seed_benchmark_dataset(),
    }
