# AIRA Backend

AIRA is an AI Recruitment and Ranking Assistant for higher education institutions. The backend analyzes student profiles, job descriptions, and recruitment requirements to support employability scoring, candidate ranking, resume optimization, skill-gap analysis, recruitment analytics, and AI-assisted recommendations.

## Stack

- FastAPI with Python 3.11
- Pydantic v2 models and schemas
- JWT authentication
- Local Ollama with Phi-3:3.8b
- FAISS-ready vector retrieval abstractions
- SQLAlchemy with future Alembic migrations
- Docker and Docker Compose deployment

## Folder Structure

- `app/api/v1`: FastAPI route modules.
- `app/auth`: authentication, JWT, password, and OAuth helpers.
- `app/core`: constants, environment loading, middleware, security, and errors.
- `app/models`: domain models used by pipelines.
- `app/schemas`: request and response schemas.
- `app/services`: scoring, ranking, analytics, feedback, resume, LLM, benchmark, ingestion, and similarity services.
- `jobs`: scheduled background job utilities.
- `rag`: document ingestion and retrieval support.
- `tests`: unit, API, and benchmark smoke tests.
- `data`: mock data, feedback memory, and FAISS index storage.

## Local Setup

Create and activate a Python 3.11 virtual environment, then install dependencies.

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Copy or update `.env`, then run the API.

```powershell
uvicorn app.main:app --reload
```

Open Swagger at `http://127.0.0.1:8000/docs`.

## Docker Setup

Build and run the API with PostgreSQL.

```powershell
docker compose up --build
```

The API listens on `http://127.0.0.1:8000`. The PostgreSQL service is optional for the current in-memory pipeline phase but is included for future persistence work.

## Ollama and Phi-3

Install Ollama locally, then pull Phi-3.

```powershell
ollama pull phi3:3.8b
ollama serve
```

The API reads `OLLAMA_URL`, `OLLAMA_MODEL`, and `OLLAMA_TIMEOUT_SECONDS` from `.env`. AI utilities are designed to degrade to deterministic local behavior where possible.

## Swagger Usage

Use Swagger to exercise these flows:

1. `GET /` to confirm the backend is running.
2. `POST /api/v1/auth/register` and `POST /api/v1/auth/login` to create and authenticate a user.
3. `POST /api/v1/student/profile` to create a student profile.
4. `POST /api/v1/scoring/profile/{profile_id}` to score a stored profile.
5. `GET /api/v1/faculty/shortlist` to retrieve ranked candidates.
6. `POST /api/v1/resume/profile/{profile_id}` to generate structured resume output.
7. `POST /api/v1/feedback/profile/{profile_id}` to generate skill-gap feedback.
8. `GET /api/v1/monitoring/` and `GET /api/v1/benchmark/` for operational checks.

## Testing

Run the default suite.

```powershell
venv\Scripts\python.exe -m pytest -q
```

Run benchmark smoke tests that are not collected by default.

```powershell
venv\Scripts\python.exe -m pytest tests\evaluation\benchmark_accuracy.py tests\evaluation\benchmark_latency.py -q
```
