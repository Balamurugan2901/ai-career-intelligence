from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.agents.skill_gap_agent import skill_gap_agent
from backend.models.database import get_db
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.skill_gap_repository import SkillGapRepository
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.skill_gap import SkillGapItem, SkillGapAnalysisResponse
from backend.utils.logger import logger

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap Analysis"])


@router.post("/analyze/{candidate_id}", response_model=SkillGapAnalysisResponse)
def analyze_skill_gaps(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Target career role name"),
    db: Session = Depends(get_db),
):
    """
    Analyzes candidate skills against market requirements for target career role,
    calculates priority matrix, persists results to SQLite DB, and returns structured summary.
    """
    logger.info(f"Analyzing skill gaps for Candidate #{candidate_id} against role '{role_name}'...")

    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    # Reconstruct CandidateProfileSchema
    if profile_record.profile_json:
        profile_schema = CandidateProfileSchema.model_validate(profile_record.profile_json)
    else:
        profile_schema = CandidateProfileSchema(
            name=profile_record.name or "Candidate",
            professional_summary=profile_record.professional_summary or "",
            years_of_experience=profile_record.years_of_experience or 0.0,
        )

    # If role_name not provided, select top matched role for candidate from DB
    if not role_name:
        paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
        role_name = paths[0].role_name if paths else "GenAI Engineer"

    # Run SkillGapAgent
    analysis_res = skill_gap_agent.analyze_candidate_gaps(
        profile=profile_schema,
        target_role=role_name,
        candidate_id=candidate_id,
    )

    # Persist gaps to DB
    SkillGapRepository.save_skill_gaps(db, candidate_id, role_name, analysis_res.gaps)

    return analysis_res


@router.get("/{candidate_id}", response_model=SkillGapAnalysisResponse)
def get_candidate_skill_gaps(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Filter by target role name"),
    db: Session = Depends(get_db),
):
    """Retrieves saved skill gap records for a candidate profile."""
    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    db_gaps = SkillGapRepository.get_skill_gaps_by_candidate_id(db, candidate_id, target_role=role_name)

    items = [
        SkillGapItem(
            skill=g.skill.name if g.skill else "Skill",
            current_level=g.current_level or "None",
            target_level=g.target_level or "Intermediate",
            priority=g.priority or "MEDIUM",
            gap_type="strength" if g.priority == "LOW" else "missing",
            reason=g.reason or "",
            estimated_learning_effort=g.estimated_learning_effort or "1-2 weeks",
            dependency_skills=g.dependency_skills or [],
        )
        for g in db_gaps
    ]

    target_role_str = role_name or (db_gaps[0].target_role if db_gaps else "GenAI Engineer")
    high_cnt = sum(1 for item in items if item.priority == "HIGH" and item.gap_type != "strength")
    med_cnt = sum(1 for item in items if item.priority == "MEDIUM" and item.gap_type != "strength")
    strength_cnt = sum(1 for item in items if item.gap_type == "strength")
    total_gaps = sum(1 for item in items if item.gap_type != "strength")

    return SkillGapAnalysisResponse(
        candidate_id=candidate_id,
        target_role=target_role_str,
        total_gaps=total_gaps,
        high_priority_count=high_cnt,
        medium_priority_count=med_cnt,
        matched_strengths_count=strength_cnt,
        gaps=items,
    )
