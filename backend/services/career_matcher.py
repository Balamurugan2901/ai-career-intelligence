from typing import List, Dict, Any
from backend.schemas.candidate import CandidateProfileSchema
from backend.services.skill_normalizer import skill_normalizer
from backend.utils.logger import logger


class CareerRoleProfile:
    """Standard reference definition for a target tech career role."""
    def __init__(self, role_name: str, required_skills: List[str], preferred_skills: List[str], min_years_exp: float = 0.0):
        self.role_name = role_name
        self.required_skills = skill_normalizer.normalize_skill_list(required_skills)
        self.preferred_skills = skill_normalizer.normalize_skill_list(preferred_skills)
        self.min_years_exp = min_years_exp


# Standard Industry Target Career Taxonomy
TARGET_ROLES: List[CareerRoleProfile] = [
    CareerRoleProfile(
        role_name="GenAI Engineer",
        required_skills=["Python", "RAG (Retrieval-Augmented Generation)", "Large Language Models", "LangChain", "Vector Databases", "FastAPI"],
        preferred_skills=["Docker", "PyTorch", "AWS", "Prompt Engineering", "ChromaDB", "Fine-Tuning"],
        min_years_exp=1.0,
    ),
    CareerRoleProfile(
        role_name="AI Engineer",
        required_skills=["Python", "Machine Learning", "Deep Learning", "PyTorch", "FastAPI", "REST APIs"],
        preferred_skills=["Docker", "AWS", "Scikit-Learn", "Computer Vision", "Natural Language Processing"],
        min_years_exp=1.0,
    ),
    CareerRoleProfile(
        role_name="ML Engineer",
        required_skills=["Python", "Machine Learning", "Scikit-Learn", "PyTorch", "SQL", "Pandas"],
        preferred_skills=["Docker", "MLOps", "Kubernetes", "AWS", "TensorFlow"],
        min_years_exp=1.0,
    ),
    CareerRoleProfile(
        role_name="Data Scientist",
        required_skills=["Python", "SQL", "Machine Learning", "Scikit-Learn", "Pandas", "Statistics"],
        preferred_skills=["PyTorch", "Deep Learning", "A/B Testing", "Tableau", "Power BI"],
        min_years_exp=1.0,
    ),
    CareerRoleProfile(
        role_name="Data Analyst",
        required_skills=["SQL", "Python", "Pandas", "Excel", "Data Visualization"],
        preferred_skills=["Tableau", "Power BI", "Statistics", "PostgreSQL"],
        min_years_exp=0.0,
    ),
    CareerRoleProfile(
        role_name="Backend Developer",
        required_skills=["Python", "FastAPI", "SQL", "PostgreSQL", "REST APIs", "Git"],
        preferred_skills=["Docker", "Redis", "AWS", "MongoDB", "Django"],
        min_years_exp=1.0,
    ),
    CareerRoleProfile(
        role_name="Software Developer",
        required_skills=["Python", "JavaScript", "SQL", "Git", "REST APIs"],
        preferred_skills=["React", "FastAPI", "Docker", "PostgreSQL", "Node.js"],
        min_years_exp=0.0,
    ),
    CareerRoleProfile(
        role_name="Computer Vision Engineer",
        required_skills=["Python", "Computer Vision", "PyTorch", "Deep Learning", "OpenCV"],
        preferred_skills=["TensorFlow", "C++", "Docker", "CUDA"],
        min_years_exp=1.0,
    ),
    CareerRoleProfile(
        role_name="NLP Engineer",
        required_skills=["Python", "Natural Language Processing", "PyTorch", "Transformers", "Large Language Models"],
        preferred_skills=["LangChain", "Vector Databases", "Scikit-Learn", "FastAPI"],
        min_years_exp=1.0,
    ),
    CareerRoleProfile(
        role_name="MLOps Engineer",
        required_skills=["Python", "Docker", "Kubernetes", "Git", "CI/CD", "AWS"],
        preferred_skills=["Machine Learning", "FastAPI", "Terraform", "MLflow", "PostgreSQL"],
        min_years_exp=1.0,
    ),
]


class CareerMatcher:
    """
    Transparent Heuristic Career Fit Scoring Engine.
    Uses deterministic mathematical weighting to calculate profile fit score:
    - Skill Match Weight: 50%
    - Experience Match Weight: 20%
    - Project Tech Match Weight: 15%
    - Education Match Weight: 10%
    - Certification Weight: 5%
    """

    @classmethod
    def calculate_role_fit(cls, profile: CandidateProfileSchema, target_role: CareerRoleProfile) -> Dict[str, Any]:
        """Calculates fit score and skill matches for a single target role."""
        candidate_skills = set(s.lower() for s in profile.skills.all_skills_list())

        # 1. Skill Match Score (50%)
        req_matched = [s for s in target_role.required_skills if s.lower() in candidate_skills]
        req_missing = [s for s in target_role.required_skills if s.lower() not in candidate_skills]
        pref_matched = [s for s in target_role.preferred_skills if s.lower() in candidate_skills]

        total_req = len(target_role.required_skills)
        req_ratio = (len(req_matched) / total_req) if total_req > 0 else 0.0
        pref_ratio = (len(pref_matched) / len(target_role.preferred_skills)) if target_role.preferred_skills else 0.0

        skill_score = min(100.0, (req_ratio * 80.0) + (pref_ratio * 20.0))

        # 2. Experience Match Score (20%)
        cand_exp = profile.years_of_experience
        req_exp = target_role.min_years_exp
        if cand_exp >= req_exp:
            exp_score = 100.0
        elif cand_exp > 0:
            exp_score = 60.0 + (cand_exp / max(req_exp, 1.0)) * 40.0
        else:
            exp_score = 30.0

        # 3. Project Match Score (15%)
        project_techs = set()
        for proj in profile.projects:
            for tech in proj.technologies_used:
                project_techs.add(tech.lower())

        proj_matched = [s for s in (target_role.required_skills + target_role.preferred_skills) if s.lower() in project_techs]
        proj_score = min(100.0, len(proj_matched) * 25.0) if proj_matched else 20.0

        # 4. Education Match Score (10%)
        edu_score = 50.0
        for edu in profile.education:
            deg = (edu.degree or "").lower()
            field = (edu.field_of_study or "").lower()
            if any(term in deg or term in field for term in ["computer science", "software", "ai", "machine learning", "data", "engineering"]):
                edu_score = 100.0
                break
            elif any(term in deg or term in field for term in ["stem", "math", "physics", "b.t", "b.s", "bachelor"]):
                edu_score = 75.0

        # 5. Certification Match Score (5%)
        cert_score = 40.0
        if len(profile.certifications) > 0:
            cert_score = min(100.0, 50.0 + len(profile.certifications) * 25.0)

        # Weighted Total Score Formula
        total_fit = round(
            (skill_score * 0.50) +
            (exp_score * 0.20) +
            (proj_score * 0.15) +
            (edu_score * 0.10) +
            (cert_score * 0.05),
            1
        )
        total_fit = max(5.0, min(98.0, total_fit))  # Bound between 5% and 98%

        all_matching = list(dict.fromkeys(req_matched + pref_matched))

        return {
            "role_name": target_role.role_name,
            "fit_score": total_fit,
            "matching_skills": all_matching,
            "missing_skills": req_missing,
            "scoring_breakdown": {
                "skill_score": round(skill_score, 1),
                "experience_score": round(exp_score, 1),
                "project_score": round(proj_score, 1),
                "education_score": round(edu_score, 1),
                "certification_score": round(cert_score, 1),
            }
        }

    @classmethod
    def evaluate_all_matches(cls, profile: CandidateProfileSchema, top_n: int = 5) -> List[Dict[str, Any]]:
        """Evaluates profile against all target roles and returns top N ranked matches."""
        results = []
        for role in TARGET_ROLES:
            match_res = cls.calculate_role_fit(profile, role)
            results.append(match_res)

        # Sort by fit_score descending
        results.sort(key=lambda x: x["fit_score"], reverse=True)
        logger.info(f"CareerMatcher evaluated {len(results)} roles for '{profile.name}'. Top match: {results[0]['role_name']} ({results[0]['fit_score']}%)")
        return results[:top_n]


career_matcher = CareerMatcher()
