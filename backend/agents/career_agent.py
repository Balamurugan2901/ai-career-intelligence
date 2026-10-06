import json
from typing import List, Optional, Dict, Any

from backend.config import settings
from backend.prompts.career.enrich_match import (
    CAREER_MATCHING_SYSTEM_INSTRUCTION,
    CAREER_MATCHING_PROMPT_TEMPLATE,
)
from backend.mcp.server import mcp_server
from backend.rag.retriever import rag_retriever
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.career import CareerPathBase, CareerMatchListResponse
from backend.services.career_matcher import career_matcher, CareerMatcher
from backend.services.llm.llm_service import LLMService, llm_service
from backend.utils.logger import logger


class CareerMatchingAgent:
    """
    Agent 2: Career Matching Agent.
    Responsible for analyzing the CandidateProfile against target career paths,
    combining transparent Python heuristic scoring with GenAI reasoning enrichment, RAG context, and MCP tools.
    """

    def __init__(self, llm_svc: Optional[LLMService] = None):
        self.llm_service = llm_svc or llm_service

    def match_career_paths(self, profile: CandidateProfileSchema, candidate_id: int = 1, top_n: int = 5) -> List[CareerPathBase]:
        """
        Evaluates candidate profile against career taxonomy, calculates transparent heuristic fit scores,
        queries RAG retriever for role knowledge, invokes MCP tools for requirements, and enriches with actionable reasoning.
        """
        logger.info(f"CareerMatchingAgent starting evaluation for '{profile.name}'...")

        # 1. Run deterministic Python heuristic scoring
        raw_matches = career_matcher.evaluate_all_matches(profile, top_n=top_n)

        # 2. Retrieve RAG domain context
        target_query = raw_matches[0]["role_name"] if raw_matches else "Artificial Intelligence"
        rag_results = rag_retriever.retrieve(query=target_query, document_type="job_description")
        context_text, sources = rag_retriever.format_context_and_sources(rag_results)
        rag_ctx_str = f"Reference Knowledge Context:\n{context_text}" if context_text else ""

        # 3. Invoke MCP Tool
        if settings.MCP_ENABLED:
            mcp_res = mcp_server.call_tool("get_role_requirements", {"role_name": target_query})
            if mcp_res.success and mcp_res.data:
                sources.append({
                    "source": mcp_res.source,
                    "tool": mcp_res.tool_name,
                    "title": f"MCP Role Requirements for {target_query}",
                })


        # 3. Enrich with LLM explanations or DEMO_MODE templates
        if settings.is_demo_mode():
            logger.info("DEMO_MODE enabled: Enriching career matches with template explanations.")
            enriched_paths = self._enrich_matches_demo(raw_matches, sources=sources)
        else:
            try:
                enriched_paths = self._enrich_matches_llm(profile, raw_matches, candidate_id, rag_context=rag_ctx_str, sources=sources)
            except Exception as e:
                logger.error(f"CareerMatchingAgent LLM call failed: {e}. Falling back to template enrichment.")
                enriched_paths = self._enrich_matches_demo(raw_matches, sources=sources)

        logger.info(f"CareerMatchingAgent completed evaluation: generated {len(enriched_paths)} ranked career matches.")
        return enriched_paths

    def _enrich_matches_llm(
        self,
        profile: CandidateProfileSchema,
        raw_matches: List[dict],
        candidate_id: int,
        rag_context: str = "",
        sources: List[Dict[str, Any]] = None,
    ) -> List[CareerPathBase]:
        """Enriches heuristic matches using LLMService with optional RAG context."""
        sources = sources or []
        prompt = CAREER_MATCHING_PROMPT_TEMPLATE.format(
            candidate_summary=profile.professional_summary,
            years_of_experience=profile.years_of_experience,
            candidate_skills=", ".join(profile.skills.all_skills_list()),
            calculated_matches_json=json.dumps(raw_matches, indent=2),
            rag_context=rag_context,
        )

        response: CareerMatchListResponse = self.llm_service.generate_json(
            prompt=prompt,
            schema=CareerMatchListResponse,
            system_instruction=CAREER_MATCHING_SYSTEM_INSTRUCTION,
        )

        # Preserve exact Python heuristic fit_scores and attach sources
        path_map = {p.role_name.lower(): p for p in response.career_paths}
        final_paths = []
        for raw in raw_matches:
            role_key = raw["role_name"].lower()
            if role_key in path_map:
                llm_item = path_map[role_key]
                final_paths.append(
                    CareerPathBase(
                        role_name=raw["role_name"],
                        fit_score=raw["fit_score"],  # Enforce Python score
                        reasoning=llm_item.reasoning,
                        matching_skills=raw["matching_skills"],
                        missing_skills=raw["missing_skills"],
                        recommended_next_step=llm_item.recommended_next_step,
                        sources=sources,
                    )
                )
            else:
                final_paths.append(self._construct_single_demo_path(raw, sources=sources))

        return final_paths

    def _enrich_matches_demo(self, raw_matches: List[dict], sources: List[Dict[str, Any]] = None) -> List[CareerPathBase]:
        """Constructs high quality fallback career path items for DEMO_MODE."""
        return [self._construct_single_demo_path(raw, sources=sources) for raw in raw_matches]

    def _construct_single_demo_path(self, raw: dict, sources: List[Dict[str, Any]] = None) -> CareerPathBase:
        """Constructs single template-enriched CareerPathBase object with source metadata."""
        sources = sources or []
        role = raw["role_name"]
        score = raw["fit_score"]
        matching = raw["matching_skills"]
        missing = raw["missing_skills"]

        if score >= 75.0:
            reasoning = f"Strong candidate profile fit ({score}% score). High overlap in core technologies ({', '.join(matching[:3])})."
            next_step = f"Focus on advanced {missing[0] if missing else 'project architecture'} to maximize industry readiness."
        elif score >= 50.0:
            reasoning = f"Moderate profile fit ({score}% score). Solid foundational skills ({', '.join(matching[:2])}) with key growth areas in {', '.join(missing[:2])}."
            next_step = f"Learn {missing[0]} and build a targeted portfolio project to close the skill gap."
        else:
            reasoning = f"Emerging profile fit ({score}% score). Candidate possesses general programming background but requires foundational training in {', '.join(missing[:3])}."
            next_step = f"Complete introductory tutorials in {missing[0] if missing else 'required tools'}."

        return CareerPathBase(
            role_name=role,
            fit_score=score,
            reasoning=reasoning,
            matching_skills=matching,
            missing_skills=missing,
            recommended_next_step=next_step,
            sources=sources,
        )


# Singleton agent instance
career_agent = CareerMatchingAgent()

