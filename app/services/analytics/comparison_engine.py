"""Student comparison helpers."""

from __future__ import annotations

from typing import Any


def compare_students(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    """Compare two student profiles across common numeric score fields."""
    numeric_fields = ["score", "cgpa", "projects", "internships", "hackathons", "achievements"]
    differences = {}
    for field in numeric_fields:
        primary_value = float(primary.get(field, 0) or 0)
        secondary_value = float(secondary.get(field, 0) or 0)
        differences[field] = round(primary_value - secondary_value, 2)

    return {
        "primary_id": primary.get("student_id") or primary.get("candidate_id"),
        "secondary_id": secondary.get("student_id") or secondary.get("candidate_id"),
        "differences": differences,
        "winner": "primary" if differences["score"] >= 0 else "secondary",
    }


def compare_against_cohort(student: dict[str, Any], cohort: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare one student against cohort averages."""
    if not cohort:
        return {"student_id": student.get("student_id"), "cohort_size": 0, "differences": {}}

    fields = ["score", "cgpa", "projects", "internships", "hackathons"]
    averages = {
        field: sum(float(item.get(field, 0) or 0) for item in cohort) / len(cohort)
        for field in fields
    }
    return {
        "student_id": student.get("student_id"),
        "cohort_size": len(cohort),
        "differences": {
            field: round(float(student.get(field, 0) or 0) - average, 2)
            for field, average in averages.items()
        },
    }


def placement_readiness(score: float) -> dict[str, object]:
    """Return placement readiness score and label."""
    if score >= 85:
        label = "excellent"
    elif score >= 70:
        label = "strong"
    elif score >= 55:
        label = "developing"
    else:
        label = "needs_improvement"
    return {"score": round(score, 2), "label": label}


def skill_distribution(students: list[dict[str, Any]]) -> dict[str, int]:
    """Return frequency of skills across a student cohort."""
    distribution: dict[str, int] = {}
    for student in students:
        for skill in student.get("skills", []):
            skill_name = str(skill).strip()
            if skill_name:
                distribution[skill_name] = distribution.get(skill_name, 0) + 1
    return dict(sorted(distribution.items(), key=lambda item: (-item[1], item[0].lower())))
