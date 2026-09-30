import json
from typing import List, Optional

from backend.config import settings
from backend.prompts.roadmap.generate_plan import (
    ROADMAP_SYSTEM_INSTRUCTION,
    ROADMAP_PROMPT_TEMPLATE,
)
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.roadmap import (
    RoadmapItemSchema,
    RoadmapPhaseSchema,
    LearningRoadmapResponse,
)
from backend.schemas.skill_gap import SkillGapItem
from backend.services.llm.llm_service import LLMService, llm_service
from backend.utils.logger import logger


class LearningRoadmapAgent:
    """
    Agent 5: Learning Roadmap Agent.
    Responsible for generating a personalized 6-phase progressive action plan
    bridging the candidate's skill gaps for their target career role.
    """

    PHASE_NAMES = [
        "Phase 1: Foundations",
        "Phase 2: Core Skills",
        "Phase 3: Advanced Skills",
        "Phase 4: Specialization & GenAI / Domain Tools",
        "Phase 5: Applied Projects & Integration",
        "Phase 6: Interview Preparation & Polish",
    ]

    def __init__(self, llm_svc: Optional[LLMService] = None):
        self.llm_service = llm_svc or llm_service

    def generate_roadmap(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        skill_gaps: List[SkillGapItem],
        candidate_id: int = 1,
    ) -> LearningRoadmapResponse:
        """Generates a personalized, progressive 6-phase learning roadmap."""
        logger.info(f"LearningRoadmapAgent generating roadmap for '{profile.name}' -> '{target_role}'...")

        if settings.is_demo_mode():
            logger.info("DEMO_MODE enabled: Returning template 6-phase roadmap.")
            return self._generate_demo_roadmap(profile, target_role, skill_gaps, candidate_id)

        try:
            gaps_data = [g.model_dump() for g in skill_gaps if g.gap_type != "strength"]
            prompt = ROADMAP_PROMPT_TEMPLATE.format(
                candidate_summary=profile.professional_summary,
                years_of_experience=profile.years_of_experience,
                candidate_skills=", ".join(profile.skills.all_skills_list()),
                target_role=target_role,
                skill_gaps_json=json.dumps(gaps_data, indent=2),
            )

            roadmap_res: LearningRoadmapResponse = self.llm_service.generate_json(
                prompt=prompt,
                schema=LearningRoadmapResponse,
                system_instruction=ROADMAP_SYSTEM_INSTRUCTION,
            )
            roadmap_res.candidate_id = candidate_id
            roadmap_res.target_role = target_role

            logger.info(f"LearningRoadmapAgent successfully generated roadmap with {len(roadmap_res.phases)} phases.")
            return roadmap_res
        except Exception as e:
            logger.error(f"LearningRoadmapAgent API call failed: {e}. Returning fallback template roadmap.")
            return self._generate_demo_roadmap(profile, target_role, skill_gaps, candidate_id)

    def _generate_demo_roadmap(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        skill_gaps: List[SkillGapItem],
        candidate_id: int,
    ) -> LearningRoadmapResponse:
        """Generates structured demo/fallback 6-phase roadmap."""
        missing_skills = [g.skill for g in skill_gaps if g.gap_type != "strength"]
        if not missing_skills:
            missing_skills = ["Python", "FastAPI", "Docker", "RAG (Retrieval-Augmented Generation)", "LangChain", "Vector Databases"]

        phases = []

        # Phase 1: Foundations
        f_skill = missing_skills[0] if len(missing_skills) > 0 else "Python"
        phases.append(
            RoadmapPhaseSchema(
                phase_number=1,
                phase_name=self.PHASE_NAMES[0],
                items=[
                    RoadmapItemSchema(
                        skill=f_skill,
                        why_it_matters=f"Essential foundation required for building scalable {target_role} applications.",
                        what_to_learn=f"Master core syntax, data structures, OOP principles, and async functions in {f_skill}.",
                        prerequisites=["Basic Programming Concepts"],
                        practical_task=f"Implement 5 core algorithms and modular utilities in {f_skill}.",
                        mini_project=f"{f_skill} Core Utility Library",
                        validation_method=f"Run unit tests verifying 100% pass rate on core utility functions.",
                        estimated_effort="15 hours",
                    )
                ],
            )
        )

        # Phase 2: Core Skills
        c_skill = missing_skills[1] if len(missing_skills) > 1 else "FastAPI"
        phases.append(
            RoadmapPhaseSchema(
                phase_number=2,
                phase_name=self.PHASE_NAMES[1],
                items=[
                    RoadmapItemSchema(
                        skill=c_skill,
                        why_it_matters=f"Core framework used industry-wide for deploying backend {target_role} services.",
                        what_to_learn=f"Route definitions, Pydantic validation, dependency injection, and error handling in {c_skill}.",
                        prerequisites=[f_skill],
                        practical_task=f"Build RESTful CRUD endpoints with input validation.",
                        mini_project=f"Production {c_skill} REST Microservice",
                        validation_method="Test endpoints with Swagger UI and pytest test client.",
                        estimated_effort="20 hours",
                    )
                ],
            )
        )

        # Phase 3: Advanced Skills
        a_skill = missing_skills[2] if len(missing_skills) > 2 else "Docker"
        phases.append(
            RoadmapPhaseSchema(
                phase_number=3,
                phase_name=self.PHASE_NAMES[2],
                items=[
                    RoadmapItemSchema(
                        skill=a_skill,
                        why_it_matters=f"Ensures reproducible deployments and containerized infrastructure for {target_role}.",
                        what_to_learn=f"Dockerfile syntax, multi-stage builds, container networks, and volume mounts.",
                        prerequisites=[c_skill],
                        practical_task=f"Containerize backend web API into docker container.",
                        mini_project=f"Containerized Multi-Container Application Setup",
                        validation_method="Verify container executes cleanly on docker run without errors.",
                        estimated_effort="15 hours",
                    )
                ],
            )
        )

        # Phase 4: Specialization & GenAI / Domain Tools
        g_skill = missing_skills[3] if len(missing_skills) > 3 else "RAG (Retrieval-Augmented Generation)"
        phases.append(
            RoadmapPhaseSchema(
                phase_number=4,
                phase_name=self.PHASE_NAMES[3],
                items=[
                    RoadmapItemSchema(
                        skill=g_skill,
                        why_it_matters=f"Key competitive differentiator for modern {target_role} roles.",
                        what_to_learn=f"Vector embeddings, similarity search, chunking strategies, and prompt engineering.",
                        prerequisites=[f_skill, c_skill],
                        practical_task=f"Build semantic document chunking and vector search pipeline.",
                        mini_project=f"Enterprise Semantic Document Q&A Engine",
                        validation_method="Evaluate retrieval accuracy across benchmark question set.",
                        estimated_effort="25 hours",
                    )
                ],
            )
        )

        # Phase 5: Applied Projects & Integration
        phases.append(
            RoadmapPhaseSchema(
                phase_number=5,
                phase_name=self.PHASE_NAMES[4],
                items=[
                    RoadmapItemSchema(
                        skill="Full-Stack Integration & Deployment",
                        why_it_matters=f"Demonstrates ability to ship end-to-end portfolio projects.",
                        what_to_learn="Connect backend REST APIs to frontend dashboard, implement CI/CD, and host application.",
                        prerequisites=[c_skill, a_skill, g_skill],
                        practical_task="Build complete portfolio project combining all learned skills.",
                        mini_project=f"End-to-End {target_role} Portfolio Application",
                        validation_method="Deploy live application and publish code to GitHub repository.",
                        estimated_effort="30 hours",
                    )
                ],
            )
        )

        # Phase 6: Interview Preparation & Polish
        phases.append(
            RoadmapPhaseSchema(
                phase_number=6,
                phase_name=self.PHASE_NAMES[5],
                items=[
                    RoadmapItemSchema(
                        skill="Technical Interview Preparation",
                        why_it_matters=f"Prepares candidate to pass technical screenings and architecture rounds for {target_role}.",
                        what_to_learn="Coding algorithms, system architecture design, STAR behavioral responses, and GenAI concepts.",
                        prerequisites=["Full-Stack Integration & Deployment"],
                        practical_task="Practice 20 coding questions and 10 mock technical interview scenarios.",
                        mini_project="Interview Answer Bank & Project Defense Brief",
                        validation_method="Conduct mock interview walkthrough explaining project architecture decisions.",
                        estimated_effort="15 hours",
                    )
                ],
            )
        )

        return LearningRoadmapResponse(
            roadmap_id=1,
            candidate_id=candidate_id,
            target_role=target_role,
            total_phases=len(phases),
            total_estimated_hours="115 hours",
            phases=phases,
        )


# Singleton agent instance
roadmap_agent = LearningRoadmapAgent()
