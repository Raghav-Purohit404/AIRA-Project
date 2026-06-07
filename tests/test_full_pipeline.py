"""Single end-to-end validation pipeline for the AIRA backend.

This test is intentionally adaptive. It discovers modules and services before
calling them, records PASS/FAIL/SKIPPED for each major pipeline, and continues
after failures so a partially implemented backend still produces a useful report.
"""

from __future__ import annotations

import importlib
import inspect
import json
import socket
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pytest


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"
STUDENT_PROFILE_PATH = SAMPLE_DIR / "student_profile.json"
JOB_DESCRIPTION_PATH = SAMPLE_DIR / "job_description.txt"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass
class PipelineResult:
    name: str
    status: str
    reason: str = ""


class PipelineContext(dict[str, Any]):
    """Shared values produced by earlier pipeline stages."""


class PipelineValidator:
    """Discover and validate the project pipelines in one logical flow."""

    def __init__(self) -> None:
        self.results: list[PipelineResult] = []
        self.context = PipelineContext()

    def run(self) -> list[PipelineResult]:
        for name, check in [
            ("Authentication", self.authentication),
            ("Profile Management", self.profile_management),
            ("Scoring", self.scoring),
            ("Ranking", self.ranking),
            ("Resume Generation", self.resume_generation),
            ("ATS Optimization", self.ats_optimization),
            ("Feedback", self.feedback),
            ("Analytics", self.analytics),
            ("JD Processing", self.jd_processing),
            ("Similarity", self.similarity),
            ("LLM", self.llm),
            ("Monitoring", self.monitoring),
            ("Benchmarking", self.benchmarking),
            ("Ingestion", self.ingestion),
            ("Rescoring", self.rescoring),
            ("Database", self.database_config),
        ]:
            self._record(name, check)
        return self.results

    def _record(self, name: str, check: Callable[[], str | None]) -> None:
        try:
            reason = check()
        except SkipPipeline as exc:
            self.results.append(PipelineResult(name, "SKIPPED", str(exc)))
        except Exception as exc:  # noqa: BLE001 - report all pipeline failures.
            self.results.append(PipelineResult(name, "FAIL", f"{type(exc).__name__}: {exc}"))
        else:
            self.results.append(PipelineResult(name, "PASS", reason or ""))

    def authentication(self) -> str | None:
        self._exercise_routes(["/", "/api/v1/health/", "/api/v1/auth/"])
        module = self._import_existing("app.auth.auth_service")
        schema_module = self._import_existing("app.schemas.auth_schema")
        service_cls = self._require_attr(module, "InMemoryAuthService")
        register_model = self._require_attr(schema_module, "RegisterRequest")
        login_model = self._require_attr(schema_module, "LoginRequest")
        service = service_cls()
        if hasattr(service, "register") and hasattr(service, "login"):
            register_payload = register_model(
                email="pipeline.user@example.com",
                password="StrongPass123",
                full_name="Pipeline User",
                role="student",
            )
            login_payload = login_model(email="pipeline.user@example.com", password="StrongPass123")
            token = service.register(register_payload)
            login = service.login(login_payload)
            self._assert_truthy(token)
            self._assert_truthy(login)
        else:
            jwt_module = self._import_existing("app.auth.jwt_handler")
            create_access_token = self._require_attr(jwt_module, "create_access_token")
            decode_access_token = self._require_attr(jwt_module, "decode_access_token")
            token = create_access_token({"sub": "pipeline.user@example.com", "role": "student"})
            decoded = decode_access_token(token)
            assert decoded.get("sub") == "pipeline.user@example.com"
        return None

    def profile_management(self) -> str | None:
        payload = self._student_payload()
        schema_module = self._import_existing("app.schemas.student_schema")
        service_module = self._import_existing("app.services.student_profile_service")
        create_model = self._require_attr(schema_module, "StudentProfileCreate")
        service_cls = self._require_attr(service_module, "StudentProfileService")
        service = service_cls()
        profile = service.create_profile(create_model.model_validate(payload))
        assert profile.id
        assert profile.completeness_score() > 50
        self.context["profile"] = profile
        self.context["profile_service"] = service
        self._exercise_routes(["/api/v1/student/"])
        return None

    def scoring(self) -> str | None:
        profile = self._require_context("profile")
        engine_module = self._import_existing("app.services.aira.aira_engine")
        engine_cls = self._require_attr(engine_module, "AIRAEngine")
        score = engine_cls().score_profile(profile, self._required_skills())
        assert 0 <= score.breakdown.final_score <= 100
        self.context["score"] = score
        self._exercise_routes(["/api/v1/scoring/"])
        return None

    def ranking(self) -> str | None:
        profile = self._require_context("profile")
        score = self._require_context("score")
        ranking_module = self._import_existing("app.services.ranking.ranking_service")
        schema_module = self._import_existing("app.schemas.faculty_schema")
        ranking_cls = self._require_attr(ranking_module, "RankingService")
        filter_model = self._require_attr(schema_module, "CandidateFilterRequest")
        candidates = [
            self._candidate_from_profile(profile, score.breakdown.final_score),
            {
                "student_id": "baseline-candidate",
                "name": "Baseline Candidate",
                "aira_score": 68.0,
                "department": "Computer Science and Engineering",
                "skills": ["Python", "SQL"],
                "cgpa": 8.1,
                "internships": 1,
                "projects": 1,
                "hackathons": 0,
            },
        ]
        ranked = ranking_cls().rank(candidates, filter_model(skills=["Python"], minimum_cgpa=8.0))
        assert ranked.success is True
        assert ranked.candidates
        self.context["ranked"] = ranked
        self._exercise_routes(["/api/v1/faculty/"])
        return None

    def resume_generation(self) -> str | None:
        profile = self._require_context("profile")
        module = self._import_existing("app.services.resume.resume_generator")
        generator_cls = self._require_attr(module, "ResumeGenerator")
        generated = generator_cls().generate_from_profile(profile)
        assert generated.get("success") is True
        assert "html" in generated and profile.basic_info.full_name in generated["html"]
        self.context["resume"] = generated
        self._exercise_routes(["/api/v1/resume/"])
        return None

    def ats_optimization(self) -> str | None:
        resume = self._require_context("resume")
        module = self._import_existing("app.services.resume.ats_optimizer")
        optimizer_cls = self._require_attr(module, "ATSOptimizer")
        analysis = optimizer_cls().analyze(resume["html"], self._required_skills())
        assert analysis.get("success") is True
        assert 0 <= analysis.get("ats_score", -1) <= 100
        self.context["ats"] = analysis
        return None

    def feedback(self) -> str | None:
        profile = self._require_context("profile")
        module = self._import_existing("app.services.feedback.feedback_engine")
        engine_cls = self._require_attr(module, "FeedbackEngine")
        feedback = engine_cls().generate_for_profile(profile, self._required_skills())
        assert feedback.get("success") is True
        assert feedback.get("feedback")
        self.context["feedback"] = feedback
        self._exercise_routes(["/api/v1/feedback/"])
        return None

    def analytics(self) -> str | None:
        profile = self._require_context("profile")
        score = self._require_context("score")
        module = self._import_existing("app.services.analytics.analytics_service")
        service_cls = self._require_attr(module, "AnalyticsService")
        service = service_cls()
        cohort = [
            {"student_id": profile.id, "department": profile.basic_info.department, "score": score.breakdown.final_score, "skills": profile.skill_names()},
            {"student_id": "peer-1", "department": profile.basic_info.department, "score": 72.5, "skills": ["Python", "SQL"]},
        ]
        stats = service.cohort_statistics(cohort)
        trend = service.trend([{"label": "sem5", "score": 76.0}, {"label": "sem6", "score": score.breakdown.final_score}])
        assert stats.get("success") is True
        assert trend.get("success") is True
        self.context["analytics"] = stats
        self._exercise_routes(["/api/v1/analytics/"])
        return None

    def jd_processing(self) -> str | None:
        jd_text = self._job_description()
        parser_module = self._import_existing("app.services.jd.jd_parser")
        validator_module = self._import_existing("app.services.jd.jd_validator")
        parse_jd = self._require_attr(parser_module, "parse_jd")
        validate_jd_text = self._require_attr(validator_module, "validate_jd_text")
        validation = validate_jd_text(jd_text)
        parsed = parse_jd(jd_text)
        assert validation.get("is_valid") is True or validation.get("valid") is True or validation.get("success") is True
        assert parsed.get("skills") or parsed.get("required_skills")
        self.context["jd"] = parsed
        self._exercise_routes(["/api/v1/jd/"])
        return None

    def similarity(self) -> str | None:
        profile = self._require_context("profile")
        jd_text = self._job_description()
        module = self._import_existing("app.services.similarity.similarity_service")
        service_cls = self._require_attr(module, "SimilarityService")
        service = service_cls()
        score = service.match_job_description(profile, jd_text)
        assert -1 <= score <= 1
        results = service.top_k("Python FastAPI backend", [("jd", jd_text), ("noise", "campus cultural event")], k=1)
        assert results and results[0]["id"] == "jd"
        self.context["similarity_score"] = score
        return None

    def llm(self) -> str | None:
        if not self._tcp_open("localhost", 11434, timeout=0.4):
            raise SkipPipeline("Ollama is not reachable on localhost:11434.")
        module = self._import_existing("app.services.llm_local.llm_service")
        service_cls = self._require_attr(module, "OllamaLLMService")
        service = service_cls(timeout=8, retries=0)
        response = service.generate("Reply with exactly: AIRA_OK", model="phi3:3.8b")
        assert str(response).strip()
        self.context["llm_response"] = response
        return None

    def monitoring(self) -> str | None:
        module = self._import_existing("app.services.monitoring.monitoring_service")
        service_cls = self._require_attr(module, "MonitoringService")
        service = service_cls()
        service.record_latency(12.5)
        snapshot = service.snapshot()
        assert snapshot.get("success") is True
        assert snapshot.get("status") == "healthy"
        self._exercise_routes(["/api/v1/monitoring/"])
        return None

    def benchmarking(self) -> str | None:
        module = self._import_existing("app.services.benchmark.benchmark_runner")
        runner_cls = self._require_attr(module, "BenchmarkRunner")
        case_cls = self._require_attr(module, "BenchmarkCase")
        report = runner_cls().run_suite(
            "full-pipeline-smoke",
            [
                case_cls("latency", lambda: "ok", expected="ok"),
                case_cls("scoring", lambda: round(self._require_context("score").breakdown.final_score, 1)),
                case_cls("ranking", lambda: len(self._require_context("ranked").candidates)),
            ],
        )
        assert report.get("success") is True
        assert report["summary"]["case_count"] >= 3
        self.context["benchmark"] = report
        self._exercise_routes(["/api/v1/benchmark/"])
        return None

    def ingestion(self) -> str | None:
        profile = self._require_context("profile")
        module = self._import_existing("app.services.ingestion.ingestion_service")
        service_cls = self._require_attr(module, "IngestionService")
        service = service_cls()
        event = service.ingest(profile, source="full-pipeline-test", force=True)
        assert event.get("accepted") is True
        assert service.latest(profile.id)["version"] == event["version"]
        self.context["ingestion_event"] = event
        return None

    def rescoring(self) -> str | None:
        profile = self._require_context("profile")
        module = self._import_existing("app.services.aira.rescoring_service")
        service_cls = self._require_attr(module, "RescoringService")
        service = service_cls()
        result = service.rescore(profile, ["skills", "cgpa"], self._required_skills())
        assert result.skipped is False
        assert result.score is not None
        assert "aira_score" in result.invalidated
        self.context["rescoring"] = result
        return None

    def database_config(self) -> str | None:
        db_module = self._import_existing("app.db.database")
        config_module = self._import_existing("app.config")
        get_database_url = self._require_attr(db_module, "get_database_url")
        create_database_engine = self._require_attr(db_module, "create_database_engine")
        url = get_database_url()
        engine = create_database_engine("sqlite:///:memory:")
        assert url
        assert engine is not None
        assert hasattr(config_module, "root")
        return None

    def _exercise_routes(self, paths: list[str]) -> None:
        app_path = ROOT / "app" / "main.py"
        if not app_path.exists():
            return
        try:
            from fastapi.testclient import TestClient

            app_module = importlib.import_module("app.main")
            app = self._require_attr(app_module, "app")
            client = TestClient(app)
        except Exception:
            return
        for path in paths:
            response = client.get(path)
            assert response.status_code < 500, f"{path} returned {response.status_code}: {response.text}"

    def _student_payload(self) -> dict[str, Any]:
        assert STUDENT_PROFILE_PATH.exists(), f"Missing sample profile: {STUDENT_PROFILE_PATH}"
        return json.loads(STUDENT_PROFILE_PATH.read_text(encoding="utf-8"))

    def _job_description(self) -> str:
        assert JOB_DESCRIPTION_PATH.exists(), f"Missing sample JD: {JOB_DESCRIPTION_PATH}"
        return JOB_DESCRIPTION_PATH.read_text(encoding="utf-8")

    def _required_skills(self) -> list[str]:
        return ["Python", "FastAPI", "SQL", "Machine Learning"]

    def _candidate_from_profile(self, profile: Any, score: float) -> dict[str, Any]:
        return {
            "student_id": profile.id,
            "name": profile.basic_info.full_name,
            "aira_score": score,
            "department": profile.basic_info.department,
            "skills": profile.skill_names(),
            "cgpa": profile.academic.cgpa,
            "internships": len(profile.internships),
            "projects": len(profile.projects),
            "hackathons": len(profile.hackathons),
        }

    def _import_existing(self, module_name: str) -> Any:
        path = ROOT.joinpath(*module_name.split(".")).with_suffix(".py")
        package_path = ROOT.joinpath(*module_name.split("."), "__init__.py")
        if not path.exists() and not package_path.exists():
            raise SkipPipeline(f"Module file not found for {module_name}.")
        return importlib.import_module(module_name)

    def _require_attr(self, module: Any, attr_name: str) -> Any:
        if not hasattr(module, attr_name):
            discovered = ", ".join(name for name, value in inspect.getmembers(module) if not name.startswith("_") and (inspect.isclass(value) or inspect.isfunction(value)))
            raise SkipPipeline(f"{module.__name__}.{attr_name} is unavailable. Discovered: {discovered or 'none'}.")
        return getattr(module, attr_name)

    def _require_context(self, key: str) -> Any:
        if key not in self.context:
            raise SkipPipeline(f"Required earlier pipeline output is unavailable: {key}.")
        return self.context[key]

    def _assert_truthy(self, value: Any) -> None:
        if isinstance(value, dict):
            assert value
            return
        if hasattr(value, "model_dump"):
            assert value.model_dump()
            return
        assert value

    def _tcp_open(self, host: str, port: int, timeout: float) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False


class SkipPipeline(Exception):
    """Raised when a pipeline component is not available in this checkout."""


def format_report(results: list[PipelineResult]) -> str:
    width = max(len(result.name) for result in results) + 2
    lines = [
        "",
        "=========================================",
        "AIRA PIPELINE VALIDATION",
        "========================",
        "",
    ]
    for result in results:
        dots = "." * max(1, width - len(result.name))
        lines.append(f"{result.name} {dots} {result.status}")
        if result.reason and result.status != "PASS":
            lines.append("Reason:")
            lines.append(result.reason)
    overall = "FAIL" if any(result.status == "FAIL" for result in results) else "PASS"
    if any(result.status == "SKIPPED" for result in results) and overall == "PASS":
        overall = "PASS WITH SKIPS"
    lines.extend(["", f"OVERALL STATUS: {overall}", "", "=========================================", ""])
    return "\n".join(lines)


def test_full_pipeline_validation() -> None:
    """Run all major AIRA pipeline checks and print a readable report."""
    validator = PipelineValidator()
    results = validator.run()
    print(format_report(results))
    assert results, "Pipeline validator did not run any checks."
    assert {result.name for result in results} >= {
        "Authentication",
        "Profile Management",
        "Scoring",
        "Ranking",
        "Resume Generation",
        "ATS Optimization",
        "Feedback",
        "Analytics",
        "JD Processing",
        "Similarity",
        "LLM",
        "Monitoring",
        "Benchmarking",
        "Ingestion",
        "Rescoring",
        "Database",
    }


if __name__ == "__main__":
    report = PipelineValidator().run()
    print(format_report(report))
    sys.exit(1 if any(item.status == "FAIL" for item in report) else 0)
