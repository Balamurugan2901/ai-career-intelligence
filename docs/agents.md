# Autonomous Multi-Agent Specifications

The platform architecture is built around **7 independent AI agents**, each dedicated to a specialized responsibility in the career growth lifecycle.

---

## Agent 1: Resume Intelligence Agent

- **File**: `backend/agents/resume_agent.py`
- **Responsibility**: Parses raw extracted resume text (PDF or DOCX) into structured Pydantic schema (`CandidateProfileSchema`).
- **Input**: Raw text string, optional filename.
- **Output**: `CandidateProfileSchema` (Name, Email, Professional Summary, Years of Experience, Education, Work Experience, Projects, Certifications, Categorized Skills, Strengths, Missing Info).
- **Fallback**: Returns structured mock candidate profile in `DEMO_MODE=true` or API failure.

---

## Agent 2: Career Matching Agent

- **File**: `backend/agents/career_agent.py` & `backend/services/career_matcher.py`
- **Responsibility**: Computes deterministic Profile Fit Scores across 9 industry roles (GenAI Engineer, AI Engineer, ML Engineer, Data Scientist, Data Analyst, Software Developer, Backend Developer, Computer Vision Engineer, MLOps Engineer).
- **Weighting**:
  - Skill Match: 50%
  - Experience Match: 20%
  - Projects: 15%
  - Education: 10%
  - Certifications: 5%
- **Input**: `CandidateProfileSchema`.
- **Output**: `List[CareerPathBase]` ranked by fit score.

---

## Agent 3: Market Intelligence Agent

- **File**: `backend/agents/market_agent.py` & `backend/services/market/`
- **Responsibility**: Fetches role demand metrics, top required core skills, emerging tooling, compensation benchmarks, and data source attribution.
- **Input**: List of role names.
- **Output**: `List[MarketRoleDemand]`.

---

## Agent 4: Skill Gap Agent

- **File**: `backend/agents/skill_gap_agent.py` & `backend/services/gap_analyzer.py`
- **Responsibility**: Maps candidate normalized skills against target role market requirements. Categorizes missing/partial skills, maps dependency prerequisites, and assigns priority (`HIGH`, `MEDIUM`, `LOW`).
- **Input**: Candidate profile, target role name.
- **Output**: `SkillGapAnalysisResponse`.

---

## Agent 5: Learning Roadmap Agent

- **File**: `backend/agents/roadmap_agent.py`
- **Responsibility**: Constructs an ordered 6-phase learning roadmap with practical tasks, mini-projects, effort hours, and validation methods.
- **Phases**:
  1. Foundations
  2. Core Skills
  3. Advanced Topics
  4. Specialization & GenAI / Domain Tools
  5. Applied Projects & System Integration
  6. Interview Preparation & Polish
- **Input**: Candidate profile, target role, prioritized skill gaps.
- **Output**: `LearningRoadmapResponse`.

---

## Agent 6: Project Recommendation Agent

- **File**: `backend/agents/project_agent.py`
- **Responsibility**: Blueprints 3 progressive portfolio projects (Beginner, Intermediate, Advanced) explicitly targeting identified candidate skill gaps.
- **Fields**: Problem statement, gap-targeting justification, tech stack tags, core features, resume talking points, and extensions.
- **Input**: Candidate profile, target role, skill gaps.
- **Output**: `ProjectRecommendationResponse`.

---

## Agent 7: Interview Preparation Agent

- **File**: `backend/agents/interview_agent.py`
- **Responsibility**: Generates targeted interview questions across 8 categories (Resume, Projects, Technical, Coding, AI/ML, GenAI, Behavioral, HR) with structural STAR answer frameworks and evaluation rubrics.
- **Input**: Candidate profile, target role, skill gaps.
- **Output**: `InterviewPreparationResponse`.
