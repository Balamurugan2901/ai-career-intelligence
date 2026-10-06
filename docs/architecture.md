# System Architecture & Technical Specifications

## 1. System Overview

The **AI Career Intelligence & Growth Platform** is a full-stack, multi-agent artificial intelligence application designed to analyze candidate profiles, perform deterministic heuristic fit scoring against industry roles, benchmark market requirements, compute priority skill gap matrices, and generate multi-phase learning roadmaps, portfolio project blueprints, and targeted interview preparation packages.

```
                  ┌─────────────────────────────────────────┐
                  │          Streamlit Dashboard UI          │
                  └────────────────────┬────────────────────┘
                                       │ HTTP REST
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │            FastAPI Web API              │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │        CareerAnalysisPipeline           │
                  │   (Orchestrator & SHA-256 Cache)       │
                  └─────┬──────────────┬──────────────┬─────┘
                        │              │              │
                        ▼              ▼              ▼
         ┌──────────────────┐  ┌──────────────┐  ┌──────────────────┐
         │ 7 Pipeline Agents│  │ Local MCP    │  │ RAG Vector Engine│
         │ (Resume..Interview) │<─┤ Server       │  │ (TF-IDF LSA SVD) │
         └─────────┬────────┘  └──────────────┘  └──────────────────┘
                   │
                   ▼
         ┌──────────────────┐           ┌──────────────────┐
         │ Gemini 2.5 Flash │           │ SQLite / DB      │
         │ (Cloud LLM API)  │           │ Persistence      │
         └──────────────────┘           └──────────────────┘
```

---

## 2. Key Architectural Principles

### 2.1 Hardware-Optimized Footprint (<50 MB RAM Peak)
Designed specifically to execute on lightweight hardware (Dual-Core CPU, 8 GB RAM, No GPU):
- **Lightweight CPU RAG**: Uses scikit-learn TF-IDF + TruncatedSVD LSA embeddings to convert text chunks into dense 64-dim vector representations. Total vector index memory consumption remains **under 50 MB RAM**.
- **In-Process Local MCP Server**: Executes Model Context Protocol tools natively within the backend process, avoiding external server container overhead and keeping memory consumption **under 10 MB RAM**.
- **Zero Local LLM Footprint**: Heavy Generative AI synthesis is delegated to remote cloud Gemini API endpoints or served via `DEMO_MODE=True` fallback templates.

### 2.2 Separation of Concerns: Python Heuristics vs. RAG Context & LLM Intelligence
- **Python Engine (Deterministic)**: Match scoring, skill normalization, skill gap calculation, priority matrix assignment, and statistical metrics are executed strictly in Python code. This prevents LLM hallucination of numerical metrics.
- **RAG Subsystem (Semantic Context)**: Retrieves reference domain knowledge (job descriptions, prerequisite trees, interview rubrics) and passes source citations to downstream agents.
- **MCP Subsystem (Structured Execution)**: Executes deterministic local queries (salary benchmarks, prerequisite trees, learning resource catalogs) with source provenance (`source: "MCP Local Reference Provider"`).
- **LLM Intelligence (Generative)**: Qualitative reasoning, contextual text extraction, learning task descriptions, project blueprint generation, and interview answer structuring are handled by Gemini API agents.

### 2.3 Token & Cost Optimization Lifecycle (>70% Token Savings)
- **Structured Pydantic Schema Passing**: Pipeline passes validated intermediate Pydantic schemas downstream instead of repeatedly re-sending raw resume text, saving over 70% in token consumption.
- **SHA-256 Pipeline Execution Cache**: `PipelineCache` hashes `(candidate_id, target_role, profile_hash)`. Re-requests for identical parameters are served instantly from cache in under 1 ms with **0 Gemini API calls**.

---

## 3. 7-Agent Sequential Pipeline Workflow

1. **Resume Intelligence Agent**: Extracts structured profile JSON (skills, experience, education, strengths, missing info) from raw PDF/DOCX text.
2. **Career Matching Agent**: Evaluates normalized candidate profile against target tech roles using weighted heuristic formula, augmented with RAG domain knowledge and MCP role requirement tools.
3. **Market Intelligence Agent**: Fetches industry demand level, emerging tooling, required core skills, and compensation benchmarks via MCP `get_market_benchmark`.
4. **Skill Gap Agent**: Computes missing/partial skills, maps prerequisite dependencies using MCP `search_skill_dependencies`, and categorizes priority (`HIGH`, `MEDIUM`, `LOW`).
5. **Learning Roadmap Agent**: Generates 6 progressive learning phases (Foundations ➔ Core ➔ Advanced ➔ GenAI ➔ Projects ➔ Interview Prep) using RAG resources and MCP `search_learning_resources`.
6. **Project Recommendation Agent**: Blueprints 3 progressive portfolio projects (Beginner, Intermediate, Advanced) targeting specific candidate skill gaps using MCP `search_jobs`.
7. **Interview Preparation Agent**: Generates tailored interview questions across 8 categories with STAR model answer frameworks using MCP `search_interview_bank`.

---

## 4. Execution State & Persistence Architecture

Execution tracking is stored in SQLite (or PostgreSQL) `analysis_runs` database table:

```
[PENDING] ➔ [RUNNING (Stage 1...7)] ➔ [COMPLETED / FAILED]
```

- **Resilience**: Transient errors trigger retries with exponential backoff via `tenacity`.
- **Sanitized Errors**: Unhandled exceptions are logged internally and sanitized at the API boundary, protecting sensitive keys and internal tracebacks.
