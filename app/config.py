from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(auth_routes.router, prefix="/api/v1/auth")
app.include_router(student_routes.router, prefix="/api/v1/student")
app.include_router(faculty_routes.router, prefix="/api/v1/faculty")
app.include_router(jd_routes.router, prefix="/api/v1/jd")
app.include_router(scoring_routes.router, prefix="/api/v1/scoring")
app.include_router(resume_routes.router, prefix="/api/v1/resume")
app.include_router(analytics_routes.router, prefix="/api/v1/analytics")
app.include_router(feedback_routes.router, prefix="/api/v1/feedback")
app.include_router(monitoring_routes.router, prefix="/api/v1/monitoring")
app.include_router(benchmark_routes.router, prefix="/api/v1/benchmark")
app.include_router(health_routes.router, prefix="/api/v1/health")


@app.get("/")
def root():
    return {
        "message": "AIRA Backend Running"
    }