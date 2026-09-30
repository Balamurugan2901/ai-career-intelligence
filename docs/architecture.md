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
        ┌─────────────────────────────────────────────────────────────┐
        │                 CareerAnalysisPipeline                      │
        │                  (Orchestration Engine)                     │
        └──────┬──────┬──────┬──────┬──────────┬──────────┬───────────┘
               │      │      │      │          │          │
               ▼      ▼      ▼      ▼          ▼          ▼
             ┌───┐  ┌───┐  ┌───┐  ┌───┐      ┌───┐      ┌───┐
             │A1 │  │A2 │  │A3 │  │A4 │      │A5 │      │A6 │ ... A7
             └───┘  └───┘  └───┘  └───┘      └───┘      └───┘
```

---

## 2. Key Architectural Principles

### 2.1 Hardware-Optimized Footprint (Zero Heavy Local LLMs)
Designed specifically to execute efficiently on standard developer machines (e.g. Dual-Core CPU, 8 GB RAM, no GPU requirement). The platform delegates heavy Generative AI reasoning to remote cloud LLM endpoints via the lightweight `google-genai` SDK or falls back seamlessly to high-fidelity mock data in `DEMO_MODE=true`.

### 2.2 Separation of Concerns: Python Heuristics vs. LLM Intelligence
- **Python Engine (Deterministic)**: Match scoring, skill normalization, skill gap calculation, priority matrix assignment, and statistical metrics are executed strictly in Python code. This prevents LLM hallucination of numerical metrics.
- **LLM Intelligence (Generative)**: Qualitative reasoning, contextual text extraction, learning task descriptions, project blueprint generation, and interview answer structuring are handled by Gemini API agents.

### 2.3 Token & Cost Optimization Lifecycle
The pipeline passes validated, structured intermediate Pydantic schemas downstream instead of repeatedly re-sending raw resume text. This reduces Gemini API token consumption by **over 70%** during complete 7-agent pipeline execution runs.

---

## 3. 7-Agent Sequential Pipeline Workflow

1. **Resume Intelligence Agent**: Extracts structured profile JSON (skills, experience, education, strengths, missing info) from raw PDF/DOCX text.
2. **Career Matching Agent**: Evaluates normalized candidate profile against 9 target tech roles using weighted heuristic formula.
3. **Market Intelligence Agent**: Fetches industry demand level, emerging tooling, required core skills, and compensation benchmarks.
4. **Skill Gap Agent**: Computes missing/partial skills, maps prerequisite dependencies, and categorizes priority (`HIGH`, `MEDIUM`, `LOW`).
5. **Learning Roadmap Agent**: Generates 6 progressive learning phases (Foundations ➔ Core ➔ Advanced ➔ GenAI ➔ Projects ➔ Interview Prep).
6. **Project Recommendation Agent**: Blueprint 3 progressive portfolio projects (Beginner, Intermediate, Advanced) targeting specific candidate skill gaps.
7. **Interview Preparation Agent**: Generates tailored interview questions across 8 categories with STAR model answer frameworks.

---

## 4. Execution State & Persistence Architecture

Execution tracking is stored in SQLite (or PostgreSQL) `analysis_runs` database table:

```
[PENDING] ➔ [RUNNING (Agent 1...7)] ➔ [COMPLETED / FAILED]
```

- **Resilience**: Transients errors trigger retries with exponential backoff via `tenacity`.
- **Sanitized Errors**: Unhandled exceptions are logged internally and sanitized at the API boundary, protecting sensitive keys and internal tracebacks.
