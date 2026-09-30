# REST API Reference Manual

The FastAPI backend server exposes RESTful HTTP endpoints for resume parsing, agent generation, pipeline orchestration, and system health checks.

Base URL: `http://127.0.0.1:8000`  
OpenAPI Documentation: `http://127.0.0.1:8000/docs`  
ReDoc UI: `http://127.0.0.1:8000/redoc`

---

## 1. System Health & Infrastructure

### `GET /health`
Returns system status, active database provider, and `DEMO_MODE` state.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "demo_mode": true,
  "database": "sqlite",
  "version": "1.0.0"
}
```

---

## 2. Resume & Profile Intelligence

### `POST /resume/upload`
Uploads candidate resume PDF or DOCX file (Max 10 MB). Parses raw text, normalizes skills, generates structured candidate profile, and persists to database.

- **Content-Type**: `multipart/form-data`
- **Body**: `file` (binary stream)

**Response `201 Created`**:
```json
{
  "resume_id": 1,
  "candidate_id": 1,
  "filename": "alex_resume.pdf",
  "file_type": ".pdf",
  "profile": {
    "name": "Alex Morgan",
    "years_of_experience": 2.5,
    "skills": { ... }
  }
}
```

### `GET /resume/candidate/{candidate_id}`
Retrieves stored candidate profile schema by candidate ID.

---

## 3. Career Path Matching

### `POST /career/match/{candidate_id}`
Runs deterministic heuristic career matching algorithm for candidate profile.

**Response `200 OK`**:
```json
[
  {
    "role_name": "GenAI Engineer",
    "fit_score": 88.0,
    "reasoning": "Strong match in Python, LangChain, PyTorch, and RAG.",
    "matching_skills": ["Python", "PyTorch", "FastAPI"],
    "missing_skills": ["Vector Databases", "vLLM"],
    "recommended_next_step": "Build a RAG portfolio project."
  }
]
```

---

## 4. Pipeline Orchestration & End-to-End Analysis

### `POST /analysis/start`
Triggers full end-to-end 7-agent sequential analysis pipeline for a candidate.

**Request Body**:
```json
{
  "candidate_id": 1,
  "target_role": "AI Engineer"
}
```

**Response `200 OK`**:
```json
{
  "analysis_id": 10,
  "candidate_id": 1,
  "resume_id": 1,
  "status": "COMPLETED",
  "execution_time_seconds": 1.85,
  "agents_completed": [
    "Resume Intelligence Agent",
    "Career Matching Agent",
    "Market Intelligence Agent",
    "Skill Gap Agent",
    "Learning Roadmap Agent",
    "Project Recommendation Agent",
    "Interview Preparation Agent"
  ]
}
```

### `GET /analysis/{analysis_id}`
Retrieves execution run tracking status by analysis ID.

### `GET /analysis/candidate/{candidate_id}/full`
Retrieves full aggregated 7-agent career intelligence summary package.

---

## 5. Agent Specific Endpoints

- `POST /market/analyze/{candidate_id}`: Market intelligence benchmark.
- `POST /skill-gap/analyze/{candidate_id}?role_name={target_role}`: Priority gap matrix.
- `POST /roadmap/generate/{candidate_id}?role_name={target_role}`: Multi-phase learning roadmap.
- `POST /projects/recommend/{candidate_id}?role_name={target_role}`: Portfolio project recommendations.
- `POST /interview/generate/{candidate_id}?role_name={target_role}`: Interview preparation questions & answer frameworks.

---

## 6. HTTP Status Code Conventions

- `200 OK`: Successful retrieval or execution.
- `201 Created`: Resource successfully created.
- `400 Bad Request`: Validation failure (corrupted file, empty file, unsupported format, oversized payload).
- `404 Not Found`: Candidate ID or Analysis ID does not exist in database.
- `500 Internal Server Error`: Sanitized error payload returned for unhandled internal exceptions.
