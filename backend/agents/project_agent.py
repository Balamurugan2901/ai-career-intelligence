import json
from typing import List, Optional, Dict, Any

from backend.config import settings
from backend.prompts.projects.suggest_projects import (
    PROJECT_RECOMMENDATION_SYSTEM_INSTRUCTION,
    PROJECT_RECOMMENDATION_PROMPT_TEMPLATE,
)
from backend.mcp.server import mcp_server
from backend.rag.retriever import rag_retriever
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.projects import ProjectItemSchema, ProjectRecommendationResponse
from backend.schemas.skill_gap import SkillGapItem
from backend.services.llm.llm_service import LLMService, llm_service
from backend.utils.logger import logger


class ProjectRecommendationAgent:
    """
    Agent 6: Project Recommendation Agent.
    Responsible for generating high-value portfolio project recommendations specifically
    designed to address and close the candidate's identified skill gaps, enriched with RAG knowledge and MCP job tools.
    """

    def __init__(self, llm_svc: Optional[LLMService] = None):
        self.llm_service = llm_svc or llm_service

    def recommend_projects(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        skill_gaps: List[SkillGapItem],
        candidate_id: int = 1,
    ) -> ProjectRecommendationResponse:
        """
        Generates 3 progressive portfolio projects (Beginner, Intermediate, Advanced)
        targeting the candidate's identified skill gaps with RAG context support and MCP tools.
        """
        logger.info(f"ProjectRecommendationAgent analyzing projects for '{profile.name}' -> '{target_role}'...")

        # Retrieve RAG domain context
        rag_results = rag_retriever.retrieve(query=target_role, document_type="project_blueprint")
        context_text, sources = rag_retriever.format_context_and_sources(rag_results)
        rag_ctx_str = f"Reference Knowledge Context:\n{context_text}" if context_text else ""

        # Invoke MCP Tool
        if settings.MCP_ENABLED:
            missing_skills = [g.skill for g in skill_gaps if g.gap_type != "strength"]
            primary_skill = missing_skills[0] if missing_skills else "Python"
            mcp_res = mcp_server.call_tool("search_jobs", {"keyword": primary_skill})
            if mcp_res.success and mcp_res.data:
                sources.append({
                    "source": mcp_res.source,
                    "tool": mcp_res.tool_name,
                    "title": f"MCP Job Benchmark Search for {primary_skill}",
                    "total_matches": mcp_res.data.get("total_matches", 0),
                })


        if settings.is_demo_mode():
            logger.info("DEMO_MODE enabled: Returning template project recommendations ladder.")
            response = self._generate_demo_projects(profile, target_role, skill_gaps, candidate_id)
            response.sources = sources
            return response

        try:
            gaps_data = [g.model_dump() for g in skill_gaps if g.gap_type != "strength"]
            prompt = PROJECT_RECOMMENDATION_PROMPT_TEMPLATE.format(
                candidate_summary=profile.professional_summary,
                candidate_skills=", ".join(profile.skills.all_skills_list()),
                target_role=target_role,
                skill_gaps_json=json.dumps(gaps_data, indent=2),
                rag_context=rag_ctx_str,
            )

            response: ProjectRecommendationResponse = self.llm_service.generate_json(
                prompt=prompt,
                schema=ProjectRecommendationResponse,
                system_instruction=PROJECT_RECOMMENDATION_SYSTEM_INSTRUCTION,
            )
            response.candidate_id = candidate_id
            response.target_role = target_role
            response.sources = sources

            # Ensure difficulty ladder validation
            response = self._validate_difficulty_ladder(response)

            logger.info(f"ProjectRecommendationAgent successfully generated {len(response.projects)} tailored project recommendations.")
            return response
        except Exception as e:
            logger.error(f"ProjectRecommendationAgent LLM call failed: {e}. Returning fallback project recommendations.")
            response = self._generate_demo_projects(profile, target_role, skill_gaps, candidate_id)
            response.sources = sources
            return response

    def _validate_difficulty_ladder(self, response: ProjectRecommendationResponse) -> ProjectRecommendationResponse:
        """Ensures projects follow progressive Beginner -> Intermediate -> Advanced ladder."""
        if len(response.projects) >= 3:
            response.projects[0].difficulty = "Beginner"
            response.projects[1].difficulty = "Intermediate"
            response.projects[2].difficulty = "Advanced"
        return response

    def _generate_demo_projects(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        skill_gaps: List[SkillGapItem],
        candidate_id: int,
    ) -> ProjectRecommendationResponse:
        """Generates realistic demo project recommendations targeting identified skill gaps."""
        missing_skills = [g.skill for g in skill_gaps if g.gap_type != "strength"]
        if not missing_skills:
            missing_skills = ["FastAPI", "RAG (Retrieval-Augmented Generation)", "LangChain", "Vector Databases", "Docker"]

        primary_gap = missing_skills[0] if missing_skills else "FastAPI"
        secondary_gap = missing_skills[1] if len(missing_skills) > 1 else "RAG (Retrieval-Augmented Generation)"
        advanced_gap = missing_skills[2] if len(missing_skills) > 2 else "Docker & Vector Databases"

        projects = [
            # 1. Beginner Project
            ProjectItemSchema(
                project_title=f"{primary_gap} Core REST API Service",
                difficulty="Beginner",
                problem_statement=f"Build a clean RESTful backend service to master {primary_gap} fundamentals and request validation.",
                why_this_project=f"Directly addresses your high-priority skill gap in {primary_gap}, establishing foundational backend proficiency.",
                skills_covered=[primary_gap, "Python", "Pydantic", "Swagger UI"],
                expected_features=[
                    f"Implement clean HTTP GET, POST, PUT, DELETE routes in {primary_gap}.",
                    "Structured Pydantic payload validation and error middleware.",
                    "Automated API documentation via OpenAPI / Swagger.",
                ],
                technology_stack=["Python", primary_gap, "Pydantic", "pytest"],
                learning_outcomes=[
                    f"Master core route handling and validation using {primary_gap}.",
                    "Gain confidence writing clean unit tests for REST endpoints.",
                ],
                resume_value=f"Demonstrates practical hands-on proficiency with {primary_gap} and clean API design principles.",
                suggested_extensions=["Add SQLite database integration using SQLAlchemy.", "Implement JWT authentication."],
            ),
            # 2. Intermediate Project
            ProjectItemSchema(
                project_title=f"Knowledge Base Semantic Search System using {secondary_gap}",
                difficulty="Intermediate",
                problem_statement=f"Develop an end-to-end document question-answering system to solve enterprise document retrieval challenges using {secondary_gap}.",
                why_this_project=f"Bridges your gap in {secondary_gap} and vector indexing, demonstrating applied AI engineering skills required for {target_role}.",
                skills_covered=[secondary_gap, "Vector Databases", primary_gap, "ChromaDB", "Python"],
                expected_features=[
                    "PDF document chunking and vector embedding pipeline.",
                    "Similarity search and context retrieval integration.",
                    "Interactive REST API backend providing accurate context-grounded answers.",
                ],
                technology_stack=["Python", primary_gap, secondary_gap, "ChromaDB", "LangChain"],
                learning_outcomes=[
                    f"Understand vector embeddings, similarity search, and RAG architectures using {secondary_gap}.",
                    "Build and optimize retrieval quality for domain documents.",
                ],
                resume_value=f"Showcases capability to design and deploy modern RAG and LLM applications using {secondary_gap}.",
                suggested_extensions=["Add web-based frontend using Streamlit or React.", "Implement metadata filtering."],
            ),
            # 3. Advanced Project
            ProjectItemSchema(
                project_title=f"Production Multi-Agent AI Platform with {advanced_gap}",
                difficulty="Advanced",
                problem_statement=f"Architect a production-grade multi-agent autonomous system with containerization, persistent storage, and background processing using {advanced_gap}.",
                why_this_project=f"Proves readiness for senior engineering responsibilities by combining {advanced_gap} with enterprise architectural patterns.",
                skills_covered=[advanced_gap, secondary_gap, primary_gap, "Docker", "PostgreSQL", "CI/CD"],
                expected_features=[
                    "Multi-agent task orchestration with retries and status monitoring.",
                    "Dockerized multi-container setup with PostgreSQL database and caching.",
                    "Comprehensive automated test suite and CI/CD workflow.",
                ],
                technology_stack=["Python", primary_gap, secondary_gap, "Docker", "PostgreSQL", "GitHub Actions"],
                learning_outcomes=[
                    "Master production container orchestration and backend system design.",
                    "Demonstrate full software engineering lifecycle proficiency for high-demand AI roles.",
                ],
                resume_value=f"Top-tier portfolio project proving production readiness for {target_role} positions.",
                suggested_extensions=["Deploy to cloud infrastructure (AWS / GCP).", "Add Prometheus metric monitoring."],
            ),
        ]

        return ProjectRecommendationResponse(
            candidate_id=candidate_id,
            target_role=target_role,
            total_projects=len(projects),
            projects=projects,
        )


# Singleton agent instance
project_agent = ProjectRecommendationAgent()

