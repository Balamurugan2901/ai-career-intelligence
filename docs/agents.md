# Autonomous Multi-Agent Specifications (RAG + MCP Architecture)

The platform architecture is built around **7 independent AI agents**, each dedicated to a specialized responsibility in the career growth lifecycle. Agents selectively leverage RAG vector context and MCP tools to enrich qualitative reasoning while maintaining deterministic Python heuristic calculations.

---

## Agent 1: Resume Intelligence Agent
- **File**: `backend/agents/resume_agent.py`
- **Responsibility**: Parses raw extracted resume text (PDF or DOCX) into structured Pydantic schema (`CandidateProfileSchema`).
- **RAG / MCP Integration**: Kept purely local and deterministic (no external tool overhead).
- **Input**: Raw text string, optional filename.
- **Output**: `CandidateProfileSchema`.

---

## Agent 2: Career Matching Agent
- **File**: `backend/agents/career_agent.py` & `backend/services/career_matcher.py`
- **Responsibility**: Computes deterministic Profile Fit Scores across 9 industry roles (GenAI Engineer, AI Engineer, ML Engineer, Data Scientist, Data Analyst, Software Developer, Backend Developer, Computer Vision Engineer, MLOps Engineer).
- **RAG Integration**: Retrieves `job_description` knowledge chunks for candidate target role to enrich LLM matching explanations.
- **MCP Integration**: Calls `get_role_requirements` to fetch reference job skill requirements and attach provenance (`source: "MCP Local Reference Provider"`).
- **Input**: `CandidateProfileSchema`.
- **Output**: `List[CareerPathBase]` with fit scores and source citations.

---

## Agent 3: Market Intelligence Agent
- **File**: `backend/agents/market_agent.py` & `backend/services/market/`
- **Responsibility**: Fetches role demand metrics, top required core skills, emerging tooling, compensation benchmarks, and data source attribution.
- **RAG Integration**: Queries domain market guides for industry context.
- **MCP Integration**: Calls `get_market_benchmark` for each requested role to supply compensation ranges and demand badges.
- **Input**: List of role names.
- **Output**: `List[MarketRoleDemand]`.

---

## Agent 4: Skill Gap Agent
- **File**: `backend/agents/skill_gap_agent.py` & `backend/services/gap_analyzer.py`
- **Responsibility**: Maps candidate normalized skills against target role requirements. Categorizes missing/partial skills, maps dependency prerequisites, and assigns priority (`HIGH`, `MEDIUM`, `LOW`).
- **RAG Integration**: Queries `skill_dependency` documents to enrich rationale explanations.
- **MCP Integration**: Calls `search_skill_dependencies` to retrieve canonical prerequisite trees for missing skills.
- **Input**: Candidate profile, target role name.
- **Output**: `SkillGapAnalysisResponse`.

---

## Agent 5: Learning Roadmap Agent
- **File**: `backend/agents/roadmap_agent.py`
- **Responsibility**: Constructs an ordered 6-phase learning roadmap with practical tasks, mini-projects, effort hours, and validation methods.
- **RAG Integration**: Queries `learning_resource` knowledge base documents.
- **MCP Integration**: Calls `search_learning_resources` to fetch verified course and book catalog citations.
- **Input**: Candidate profile, target role, prioritized skill gaps.
- **Output**: `LearningRoadmapResponse`.

---

## Agent 6: Project Recommendation Agent
- **File**: `backend/agents/project_agent.py`
- **Responsibility**: Blueprints 3 progressive portfolio projects (Beginner, Intermediate, Advanced) explicitly targeting identified candidate skill gaps.
- **RAG Integration**: Queries `project_blueprint` knowledge documents.
- **MCP Integration**: Calls `search_jobs` to verify real-world industry application alignment for project specifications.
- **Input**: Candidate profile, target role, skill gaps.
- **Output**: `ProjectRecommendationResponse`.

---

## Agent 7: Interview Preparation Agent
- **File**: `backend/agents/interview_agent.py`
- **Responsibility**: Generates targeted interview questions across 8 categories with structural STAR answer frameworks and evaluation rubrics.
- **RAG Integration**: Queries `interview_bank` reference question documents.
- **MCP Integration**: Calls `search_interview_bank` to retrieve category questions and evaluation rubrics.
- **Input**: Candidate profile, target role, skill gaps.
- **Output**: `InterviewPreparationResponse`.
