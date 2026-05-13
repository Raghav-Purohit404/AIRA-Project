from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import health_routes

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

# ROUTES
app.include_router(
    health_routes.router,
    prefix="/api/v1/health"
)

@app.get("/")
def root():
    return {
        "message": "AIRA Backend Running"
    }
