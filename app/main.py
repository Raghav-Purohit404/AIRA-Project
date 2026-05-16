from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import analytics_routes

from app.api.v1 import (
    auth_routes,
    student_routes,
    faculty_routes,
    jd_routes,
    scoring_routes,
    resume_routes,
    analytics_routes,
    feedback_routes,
    monitoring_routes,
    benchmark_routes,
    health_routes
)

app = FastAPI(
    title="AIRA Backend",
    version="1.0.0"
)

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROOT ROUTE
# =========================

@app.get("/")
def root():

    return {
        "success": True,
        "message": "AIRA Backend Running"
    }

# =========================
# ROUTERS
# =========================

app.include_router(
    auth_routes.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    student_routes.router,
    prefix="/api/v1/student",
    tags=["Student"]
)

app.include_router(
    faculty_routes.router,
    prefix="/api/v1/faculty",
    tags=["Faculty"]
)

app.include_router(
    jd_routes.router,
    prefix="/api/v1/jd",
    tags=["Job Description"]
)

app.include_router(
    scoring_routes.router,
    prefix="/api/v1/scoring",
    tags=["Scoring"]
)

app.include_router(
    resume_routes.router,
    prefix="/api/v1/resume",
    tags=["Resume"]
)

app.include_router(
    analytics_routes.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

app.include_router(
    feedback_routes.router,
    prefix="/api/v1/feedback",
    tags=["Feedback"]
)

app.include_router(
    monitoring_routes.router,
    prefix="/api/v1/monitoring",
    tags=["Monitoring"]
)

app.include_router(
    benchmark_routes.router,
    prefix="/api/v1/benchmark",
    tags=["Benchmark"]
)

app.include_router(
    health_routes.router,
    prefix="/api/v1/health",
    tags=["Health"]
)