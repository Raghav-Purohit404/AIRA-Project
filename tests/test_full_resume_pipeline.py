"""API-level integration coverage for AIRA's real resume-to-PDF workflow."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.main import app


ROOT = Path(__file__).resolve().parent
RAW_PROFILE_PATH = ROOT / "sample_data" / "raw_student_profile.json"
JD_PATH = ROOT / "sample_data" / "sample_job_description.json"
OUTPUT_PATH = ROOT / "output" / "generated_resume.pdf"


def _load_json(path: Path) -> dict[str, object]:
    """Load a checked-in API fixture with an explicit failure message."""
    assert path.is_file(), f"Missing integration fixture: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def _pdf_text(pdf_bytes: bytes) -> tuple[int, str]:
    """Extract selectable text from the actual PDF response."""
    reader = PdfReader(BytesIO(pdf_bytes))
    return len(reader.pages), "\n".join(page.extract_text() or "" for page in reader.pages)


def test_raw_student_to_final_pdf_through_fastapi() -> None:
    """Turn raw synthetic data into a real, parseable resume PDF via FastAPI."""
    raw_profile = _load_json(RAW_PROFILE_PATH)
    jd_fixture = _load_json(JD_PATH)
    jd_text = str(jd_fixture["text"])

    with TestClient(app) as client:
        # Raw JSON is validated by StudentProfileCreate and persisted by the
        # actual profile route before any downstream route consumes it.
        create_response = client.post("/api/v1/student/profile", json=raw_profile)
        assert create_response.status_code == 200, create_response.text
        profile = create_response.json()["profile"]
        profile_id = profile["id"]
        assert profile["basic_info"]["full_name"] == "Maya Iyer"

        jd_response = client.post("/api/v1/jd/parse", json={"text": jd_text})
        assert jd_response.status_code == 200, jd_response.text
        required_skills = jd_response.json()["job_description"]["required_skills"]
        assert required_skills

        score_response = client.post(
            f"/api/v1/scoring/profile/{profile_id}",
            json={"required_skills": required_skills},
        )
        assert score_response.status_code == 200, score_response.text
        assert 0 <= score_response.json()["score"]["breakdown"]["final_score"] <= 100

        feedback_response = client.post(
            f"/api/v1/feedback/profile/{profile_id}",
            json={"target_skills": required_skills},
        )
        assert feedback_response.status_code == 200, feedback_response.text
        feedback = feedback_response.json()["feedback"]
        assert feedback["strengths"] or feedback["recommendations"]

        ranking_response = client.get("/api/v1/faculty/shortlist", params=[("skills", "Python")])
        assert ranking_response.status_code == 200, ranking_response.text
        assert profile_id in [candidate["student_id"] for candidate in ranking_response.json()["candidates"]]

        # This real route runs the canonical resume projection, JD-aware ATS
        # analysis, HTML template, and ReportLab renderer, then streams the file.
        pdf_response = client.post(
            "/api/v1/resume/generate",
            json={"profile": profile, "template": "ats", "job_description": jd_text, "use_llm_enrichment": False},
        )
        assert pdf_response.status_code == 200, pdf_response.text
        assert pdf_response.headers["content-type"].startswith("application/pdf")
        assert 0 <= float(pdf_response.headers["x-aira-ats-score"]) <= 100

        artifact_path = Path(pdf_response.headers["x-aira-resume-path"])
        assert artifact_path.is_file() and artifact_path.stat().st_size > 0
        assert pdf_response.content == artifact_path.read_bytes()
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_bytes(pdf_response.content)
        assert OUTPUT_PATH.is_file() and OUTPUT_PATH.stat().st_size > 0

    page_count, text = _pdf_text(pdf_response.content)
    assert page_count >= 2
    normalized_text = text.casefold()
    for required_text in (
        "Maya Iyer", "Professional Summary", "Technical Skills", "Education",
        "Experience", "Projects", "Certifications", "Achievements",
        "Research & Publications", "Leadership & Activities",
        "Campus Placement Intelligence Platform",
        "Longitudinal Skills Evidence and Interview Preparation Workspace",
        "PostgreSQL", "Institute of Advanced Computing and Applied Engineering",
    ):
        assert required_text.casefold() in normalized_text
    assert "long project evidence sentence with validated implementation detail" in normalized_text
    assert "kubernetes" not in normalized_text
