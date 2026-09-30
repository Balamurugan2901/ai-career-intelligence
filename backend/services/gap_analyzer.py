from typing import List, Dict, Any, Set
from backend.schemas.candidate import CandidateProfileSchema
from backend.services.career_matcher import TARGET_ROLES, CareerRoleProfile
from backend.services.market.market_service import market_service
from backend.services.skill_normalizer import skill_normalizer
from backend.utils.logger import logger


# Standard Skill Dependency Tree
SKILL_DEPENDENCIES: Dict[str, List[str]] = {
    "rag (retrieval-augmented generation)": ["Python", "Vector Databases"],
    "langchain": ["Python", "FastAPI"],
    "llamaindex": ["Python", "RAG (Retrieval-Augmented Generation)"],
    "pytorch": ["Python", "Machine Learning"],
    "tensorflow": ["Python", "Machine Learning"],
    "scikit-learn": ["Python", "Machine Learning"],
    "computer vision": ["Python", "PyTorch"],
    "natural language processing": ["Python", "PyTorch"],
    "mlops": ["Docker", "Python", "Git"],
    "kubernetes": ["Docker"],
    "fastapi": ["Python", "REST APIs"],
    "react": ["JavaScript"],
    "postgresql": ["SQL"],
}


class GapAnalyzer:
    """
    Deterministic Skill Gap & Priority Matrix Engine.
    Compares candidate profile skills against market demands for a target role.
    Categorizes skills into missing, partial, or strength, and computes priority levels.
    """

    @classmethod
    def analyze_gaps(cls, profile: CandidateProfileSchema, target_role_name: str) -> List[Dict[str, Any]]:
        """
        Determines deterministic skill gaps and strengths for candidate against target role.
        """
        # 1. Look up role definition from target roles or market service
        role_profile = cls._get_role_profile(target_role_name)
        req_skills = set(s.lower() for s in role_profile.required_skills)
        pref_skills = set(s.lower() for s in role_profile.preferred_skills)

        # 2. Extract normalized candidate skills
        cand_skills_raw = profile.skills.all_skills_list()
        cand_skills_norm = set(skill_normalizer.normalize_skill(s).lower() for s in cand_skills_raw)

        gap_items: List[Dict[str, Any]] = []

        # 3. Process Required & Preferred Target Role Skills
        all_target_skills = list(dict.fromkeys(role_profile.required_skills + role_profile.preferred_skills))

        for raw_skill in all_target_skills:
            norm_skill = skill_normalizer.normalize_skill(raw_skill)
            skill_lower = norm_skill.lower()
            deps = SKILL_DEPENDENCIES.get(skill_lower, [])

            if skill_lower in cand_skills_norm:
                # STRENGTH: Candidate already possesses this skill
                gap_items.append({
                    "skill": norm_skill,
                    "current_level": "Intermediate",
                    "target_level": "Intermediate",
                    "priority": "LOW",
                    "gap_type": "strength",
                    "reason": f"Existing candidate strength matching {target_role_name} requirements.",
                    "estimated_learning_effort": "Already Covered",
                    "dependency_skills": deps,
                })
            else:
                # MISSING or PARTIAL
                is_required = skill_lower in req_skills
                priority = "HIGH" if is_required else "MEDIUM"
                
                # Check if it is a foundational prerequisite for other gaps
                if any(skill_lower in [d.lower() for d in deps_list] for deps_list in SKILL_DEPENDENCIES.values()):
                    priority = "HIGH"

                effort = "2-3 weeks" if is_required else "1-2 weeks"

                gap_items.append({
                    "skill": norm_skill,
                    "current_level": "None",
                    "target_level": "Intermediate" if not is_required else "Advanced",
                    "priority": priority,
                    "gap_type": "missing",
                    "reason": f"High-demand requirement for {target_role_name} role.",
                    "estimated_learning_effort": effort,
                    "dependency_skills": deps,
                })

        logger.info(f"GapAnalyzer evaluated {len(gap_items)} skills for '{profile.name}' against role '{target_role_name}'.")
        return gap_items

    @classmethod
    def _get_role_profile(cls, role_name: str) -> CareerRoleProfile:
        """Finds target role profile or constructs one from market service data."""
        for role in TARGET_ROLES:
            if role.role_name.lower() == role_name.lower():
                return role

        # Fallback query from market service
        mkt_data = market_service.get_role_demand(role_name)
        return CareerRoleProfile(
            role_name=role_name,
            required_skills=mkt_data.get("top_required_skills", ["Python", "SQL"]),
            preferred_skills=mkt_data.get("emerging_skills", ["Docker"]),
            min_years_exp=1.0,
        )


gap_analyzer = GapAnalyzer()
