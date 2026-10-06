import json
from typing import List, Optional, Dict, Any

from backend.config import settings
from backend.prompts.interview.generate_questions import (
    INTERVIEW_PREP_SYSTEM_INSTRUCTION,
    INTERVIEW_PREP_PROMPT_TEMPLATE,
)
from backend.mcp.server import mcp_server
from backend.rag.retriever import rag_retriever
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.interview import (
    InterviewQuestionItemSchema,
    InterviewCategorySchema,
    InterviewPreparationResponse,
)
from backend.schemas.skill_gap import SkillGapItem
from backend.services.llm.llm_service import LLMService, llm_service
from backend.utils.logger import logger


class InterviewPreparationAgent:
    """
    Agent 7: Interview Preparation Agent.
    Responsible for generating custom interview preparation questions across 8 categories,
    tailored to the candidate's resume, projects, target role skill gaps, RAG interview context, and MCP tools.
    """

    CATEGORIES = [
        "Resume Questions",
        "Project Questions",
        "Technical Questions",
        "Coding Questions",
        "AI/ML Questions",
        "GenAI Questions",
        "Behavioral Questions",
        "HR Questions",
    ]

    def __init__(self, llm_svc: Optional[LLMService] = None):
        self.llm_service = llm_svc or llm_service

    def generate_interview_prep(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        skill_gaps: List[SkillGapItem],
        candidate_id: int = 1,
    ) -> InterviewPreparationResponse:
        """
        Generates tailored interview preparation questions grouped by category with RAG context support and MCP tools.
        """
        logger.info(f"InterviewPreparationAgent generating questions for '{profile.name}' -> '{target_role}'...")

        # Retrieve RAG domain context
        rag_results = rag_retriever.retrieve(query=target_role, document_type="interview_bank")
        context_text, sources = rag_retriever.format_context_and_sources(rag_results)
        rag_ctx_str = f"Reference Knowledge Context:\n{context_text}" if context_text else ""

        # Invoke MCP Tool
        if settings.MCP_ENABLED:
            mcp_res = mcp_server.call_tool("search_interview_bank", {"category": "GenAI Questions", "role_name": target_role})
            if mcp_res.success and mcp_res.data:
                sources.append({
                    "source": mcp_res.source,
                    "tool": mcp_res.tool_name,
                    "title": f"MCP Interview Bank for {target_role}",
                    "total_questions": mcp_res.data.get("total_questions", 0),
                })


        if settings.is_demo_mode():
            logger.info("DEMO_MODE enabled: Returning template interview preparation package.")
            prep_res = self._generate_demo_interview_prep(profile, target_role, skill_gaps, candidate_id)
            prep_res.sources = sources
            return prep_res

        try:
            proj_summary = ", ".join(p.title for p in profile.projects) if profile.projects else "None specified"
            gaps_data = [g.model_dump() for g in skill_gaps if g.gap_type != "strength"]

            prompt = INTERVIEW_PREP_PROMPT_TEMPLATE.format(
                candidate_summary=profile.professional_summary,
                years_of_experience=profile.years_of_experience,
                candidate_skills=", ".join(profile.skills.all_skills_list()),
                candidate_projects=proj_summary,
                target_role=target_role,
                skill_gaps_json=json.dumps(gaps_data, indent=2),
                rag_context=rag_ctx_str,
            )

            prep_res: InterviewPreparationResponse = self.llm_service.generate_json(
                prompt=prompt,
                schema=InterviewPreparationResponse,
                system_instruction=INTERVIEW_PREP_SYSTEM_INSTRUCTION,
            )
            prep_res.candidate_id = candidate_id
            prep_res.target_role = target_role
            prep_res.sources = sources

            logger.info(f"InterviewPreparationAgent successfully generated {prep_res.total_questions} interview questions across {len(prep_res.categories)} categories.")
            return prep_res
        except Exception as e:
            logger.error(f"InterviewPreparationAgent LLM call failed: {e}. Returning fallback interview prep package.")
            prep_res = self._generate_demo_interview_prep(profile, target_role, skill_gaps, candidate_id)
            prep_res.sources = sources
            return prep_res

    def _generate_demo_interview_prep(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        skill_gaps: List[SkillGapItem],
        candidate_id: int,
    ) -> InterviewPreparationResponse:
        """Generates realistic demo interview preparation package covering all 8 categories."""
        first_proj_title = profile.projects[0].title if profile.projects else "RAG Document Search System"
        missing_skills = [g.skill for g in skill_gaps if g.gap_type != "strength"]
        top_gap = missing_skills[0] if missing_skills else "LangChain"

        categories = [
            # 1. Resume Questions
            InterviewCategorySchema(
                category_name="Resume Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question=f"Can you walk me through your background and explain what motivated your pivot towards a {target_role} position?",
                        category="Resume Questions",
                        difficulty="Mid-Level",
                        expected_concepts=["Career Progression", "Tech Skill Evolution", "Role Motivation"],
                        evaluation_points=[
                            "Clear, concise narrative summarizing past technical experience.",
                            "Logical justification connecting past software skills to target role requirements.",
                        ],
                        model_answer_structure="1. Executive Summary of past background -> 2. Key transition trigger / project experience -> 3. Target role alignment.",
                    )
                ],
            ),
            # 2. Project Questions
            InterviewCategorySchema(
                category_name="Project Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question=f"In your project '{first_proj_title}', what were the key architectural trade-offs you made during system design?",
                        category="Project Questions",
                        difficulty="Mid-Level",
                        expected_concepts=["System Architecture", "Trade-Off Analysis", "Performance Optimization"],
                        evaluation_points=[
                            "Understands trade-offs between latency, accuracy, and operational cost.",
                            "Explains concrete bottleneck resolution with quantifiable metrics.",
                        ],
                        model_answer_structure="1. System context & objective -> 2. Architectural option A vs B -> 3. Final choice and measured impact.",
                    )
                ],
            ),
            # 3. Technical Questions
            InterviewCategorySchema(
                category_name="Technical Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question=f"How would you design a scalable RESTful backend service using Python and FastAPI for high-concurrency requests?",
                        category="Technical Questions",
                        difficulty="Senior",
                        expected_concepts=["Async I/O", "Concurrency", "Database Connection Pooling", "FastAPI"],
                        evaluation_points=[
                            "Explains async/await event loop mechanics vs multi-threading.",
                            "Discusses database connection pooling and caching strategies with Redis.",
                        ],
                        model_answer_structure="1. Async event loop explanation -> 2. Non-blocking database I/O -> 3. Load balancing and caching strategy.",
                    )
                ],
            ),
            # 4. Coding Questions
            InterviewCategorySchema(
                category_name="Coding Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question="Given a large list of string documents, write an optimal algorithm in Python to compute term frequency and return top K keywords.",
                        category="Coding Questions",
                        difficulty="Mid-Level",
                        expected_concepts=["Hash Maps (Counter)", "Min-Heap / Priority Queue", "Time & Space Complexity"],
                        evaluation_points=[
                            "Identifies O(N log K) heap-based optimization over full O(N log N) sort.",
                            "Writes clean, Pythonic code handling edge cases.",
                        ],
                        model_answer_structure="1. Clarify constraints -> 2. Outline Heap + Hash Map approach -> 3. Code solution & analyze space/time complexity.",
                    )
                ],
            ),
            # 5. AI/ML Questions
            InterviewCategorySchema(
                category_name="AI/ML Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question="Explain the bias-variance tradeoff in Machine Learning and how you prevent overfitting in production models.",
                        category="AI/ML Questions",
                        difficulty="Mid-Level",
                        expected_concepts=["Underfitting vs Overfitting", "Regularization (L1/L2)", "Cross-Validation"],
                        evaluation_points=[
                            "Accurately defines bias and variance components of model generalization error.",
                            "Lists practical regularization techniques (L2, Dropout, Early Stopping).",
                        ],
                        model_answer_structure="1. Conceptual definition -> 2. Causes of overfitting -> 3. Mitigation strategies in pipeline.",
                    )
                ],
            ),
            # 6. GenAI Questions
            InterviewCategorySchema(
                category_name="GenAI Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question=f"How does a Retrieval-Augmented Generation (RAG) system work, and how would you resolve hallucinations when using {top_gap}?",
                        category="GenAI Questions",
                        difficulty="Senior",
                        expected_concepts=["RAG Architecture", "Vector Embeddings", "Prompt Guardrails", "Context Grounding"],
                        evaluation_points=[
                            "Describes indexing, retrieval, and generation stages clearly.",
                            "Explains context compression, reranking, and system prompt constraints to eliminate hallucinations.",
                        ],
                        model_answer_structure="1. RAG pipeline flow -> 2. Root cause of hallucinations -> 3. Advanced retrieval tuning & prompt guardrails.",
                    )
                ],
            ),
            # 7. Behavioral Questions
            InterviewCategorySchema(
                category_name="Behavioral Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question="Tell me about a time when you encountered a critical bug or production outage right before a deployment deadline.",
                        category="Behavioral Questions",
                        difficulty="Mid-Level",
                        expected_concepts=["Root Cause Diagnosis", "Pressure Management", "Team Communication"],
                        evaluation_points=[
                            "Demonstrates methodical debugging under pressure.",
                            "Highlights team collaboration, ownership, and post-mortem prevention.",
                        ],
                        model_answer_structure="STAR Method: Situation -> Task -> Action -> Result & Retrospective.",
                    )
                ],
            ),
            # 8. HR Questions
            InterviewCategorySchema(
                category_name="HR Questions",
                questions=[
                    InterviewQuestionItemSchema(
                        question=f"Where do you see your technical career progressing over the next 2-3 years in the {target_role} domain?",
                        category="HR Questions",
                        difficulty="Junior",
                        expected_concepts=["Career Growth", "Ownership", "Continuous Learning"],
                        evaluation_points=[
                            "Shows genuine enthusiasm for technical growth and domain specialization.",
                            "Aligns personal growth goals with engineering impact.",
                        ],
                        model_answer_structure="1. Immediate 12-month technical impact -> 2. Mid-term leadership/ownership expansion -> 3. Alignment with company vision.",
                    )
                ],
            ),
        ]

        total_q = sum(len(c.questions) for c in categories)

        return InterviewPreparationResponse(
            candidate_id=candidate_id,
            target_role=target_role,
            total_questions=total_q,
            categories=categories,
        )


# Singleton agent instance
interview_agent = InterviewPreparationAgent()

