import json
from typing import List, Optional

from backend.config import settings
from backend.prompts.skill_gap.analyze_gaps import (
    SKILL_GAP_SYSTEM_INSTRUCTION,
    SKILL_GAP_PROMPT_TEMPLATE,
)
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.skill_gap import SkillGapItem, SkillGapAnalysisResponse
from backend.services.gap_analyzer import gap_analyzer, GapAnalyzer
from backend.services.llm.llm_service import LLMService, llm_service
from backend.utils.logger import logger


class SkillGapAgent:
    """
    Agent 4: Skill Gap Agent.
    Responsible for analyzing gaps between Candidate Profile skills and Target Role Market requirements.
    Calculates priority matrix, categorizes gaps, and generates structured learning effort metrics.
    """

    def __init__(self, llm_svc: Optional[LLMService] = None):
        self.llm_service = llm_svc or llm_service

    def analyze_candidate_gaps(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        candidate_id: int = 1,
    ) -> SkillGapAnalysisResponse:
        """
        Runs deterministic gap matrix analysis, enriches with GenAI rationale, and calculates summary metrics.
        """
        logger.info(f"SkillGapAgent starting gap analysis for '{profile.name}' against '{target_role}'...")

        # 1. Run deterministic gap matrix engine
        raw_gaps = gap_analyzer.analyze_gaps(profile, target_role)

        # 2. Enrich with LLM rationale or fallback
        if settings.is_demo_mode():
            logger.info("DEMO_MODE enabled: Using template gap enrichment.")
            enriched_items = self._enrich_gaps_demo(raw_gaps, target_role)
        else:
            try:
                enriched_items = self._enrich_gaps_llm(profile, target_role, raw_gaps, candidate_id)
            except Exception as e:
                logger.error(f"SkillGapAgent LLM call failed: {e}. Falling back to template enrichment.")
                enriched_items = self._enrich_gaps_demo(raw_gaps, target_role)

        # 3. Compute summary counts
        high_cnt = sum(1 for g in enriched_items if g.priority == "HIGH" and g.gap_type != "strength")
        med_cnt = sum(1 for g in enriched_items if g.priority == "MEDIUM" and g.gap_type != "strength")
        strength_cnt = sum(1 for g in enriched_items if g.gap_type == "strength")
        total_gaps = sum(1 for g in enriched_items if g.gap_type != "strength")

        response = SkillGapAnalysisResponse(
            candidate_id=candidate_id,
            target_role=target_role,
            total_gaps=total_gaps,
            high_priority_count=high_cnt,
            medium_priority_count=med_cnt,
            matched_strengths_count=strength_cnt,
            gaps=enriched_items,
        )

        logger.info(
            f"SkillGapAgent completed analysis for '{target_role}': "
            f"{total_gaps} gaps ({high_cnt} High, {med_cnt} Med), {strength_cnt} Strengths."
        )
        return response

    def _enrich_gaps_llm(
        self,
        profile: CandidateProfileSchema,
        target_role: str,
        raw_gaps: List[dict],
        candidate_id: int,
    ) -> List[SkillGapItem]:
        """Enriches gap items using LLMService."""
        prompt = SKILL_GAP_PROMPT_TEMPLATE.format(
            candidate_summary=profile.professional_summary,
            candidate_skills=", ".join(profile.skills.all_skills_list()),
            target_role=target_role,
            deterministic_gaps_json=json.dumps(raw_gaps, indent=2),
        )

        res: SkillGapAnalysisResponse = self.llm_service.generate_json(
            prompt=prompt,
            schema=SkillGapAnalysisResponse,
            system_instruction=SKILL_GAP_SYSTEM_INSTRUCTION,
        )

        # Preserve exact Python deterministic matrix classifications
        llm_map = {g.skill.lower(): g for g in res.gaps}
        final_items = []
        for raw in raw_gaps:
            s_key = raw["skill"].lower()
            if s_key in llm_map:
                llm_g = llm_map[s_key]
                final_items.append(
                    SkillGapItem(
                        skill=raw["skill"],
                        current_level=raw["current_level"],
                        target_level=raw["target_level"],
                        priority=raw["priority"],
                        gap_type=raw["gap_type"],
                        reason=llm_g.reason,
                        estimated_learning_effort=llm_g.estimated_learning_effort,
                        dependency_skills=raw["dependency_skills"],
                    )
                )
            else:
                final_items.append(self._construct_single_demo_item(raw, target_role))

        return final_items

    def _enrich_gaps_demo(self, raw_gaps: List[dict], target_role: str) -> List[SkillGapItem]:
        """Constructs fallback template enriched gap items for DEMO_MODE."""
        return [self._construct_single_demo_item(raw, target_role) for raw in raw_gaps]

    def _construct_single_demo_item(self, raw: dict, target_role: str) -> SkillGapItem:
        """Constructs single template-enriched SkillGapItem object."""
        skill = raw["skill"]
        gap_type = raw["gap_type"]
        priority = raw["priority"]
        deps = raw["dependency_skills"]

        if gap_type == "strength":
            reason = f"Candidate already possesses strong proficiency in {skill}, matching {target_role} requirements."
            effort = "Covered"
        elif priority == "HIGH":
            reason = f"Critical core requirement for {target_role}. Mastery is essential for building production systems."
            effort = "2-3 weeks"
        else:
            reason = f"Valuable secondary skill for {target_role} improving project delivery and workflow efficiency."
            effort = "1-2 weeks"

        return SkillGapItem(
            skill=skill,
            current_level=raw["current_level"],
            target_level=raw["target_level"],
            priority=priority,
            gap_type=gap_type,
            reason=reason,
            estimated_learning_effort=effort,
            dependency_skills=deps,
        )


# Singleton agent instance
skill_gap_agent = SkillGapAgent()
