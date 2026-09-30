from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.agents.interview_agent import interview_agent
from backend.agents.skill_gap_agent import skill_gap_agent
from backend.models.database import get_db
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.interview_repository import InterviewRepository
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.interview import (
    InterviewQuestionItemSchema,
    InterviewCategorySchema,
    InterviewPreparationResponse,
)
from backend.utils.logger import logger

router = APIRouter(prefix="/interview", tags=["Interview Preparation"])


@router.post("/generate/{candidate_id}", response_model=InterviewPreparationResponse)
def generate_interview_preparation(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Target career role name"),
    db: Session = Depends(get_db),
):
    """
    Generates tailored interview preparation questions across 8 categories,
    focusing on candidate background, projects, and target role skill gaps.
    Persists package to SQLite DB and returns structured response.
    """
    logger.info(f"Generating interview preparation package for Candidate #{candidate_id}...")

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

    # Determine target role
    if not role_name:
        paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
        role_name = paths[0].role_name if paths else "GenAI Engineer"

    # Analyze gaps
    gap_response = skill_gap_agent.analyze_candidate_gaps(
        profile=profile_schema,
        target_role=role_name,
        candidate_id=candidate_id,
    )

    # Generate Interview Preparation Package
    prep_res = interview_agent.generate_interview_prep(
        profile=profile_schema,
        target_role=role_name,
        skill_gaps=gap_response.gaps,
        candidate_id=candidate_id,
    )

    # Persist to Database
    InterviewRepository.save_interview_questions(db, candidate_id, prep_res.categories)

    return prep_res


@router.get("/{candidate_id}", response_model=InterviewPreparationResponse)
def get_candidate_interview_preparation(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Filter target role name"),
    db: Session = Depends(get_db),
):
    """Retrieves saved interview preparation questions grouped by category for a candidate profile."""
    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    db_questions = InterviewRepository.get_interview_questions_by_candidate_id(db, candidate_id)
    if not db_questions:
        # Fallback to generating prep package if not yet stored
        paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
        target_role_str = role_name or (paths[0].role_name if paths else "GenAI Engineer")
        return generate_interview_preparation(candidate_id, role_name=target_role_str, db=db)

    # Group questions by category
    cat_dict: Dict[str, List[InterviewQuestionItemSchema]] = {}

    for iq in db_questions:
        cat = iq.category or "Technical Questions"
        if cat not in cat_dict:
            cat_dict[cat] = []

        cat_dict[cat].append(
            InterviewQuestionItemSchema(
                question=iq.question,
                category=cat,
                difficulty=iq.difficulty or "Mid-Level",
                expected_concepts=iq.expected_concepts or [],
                evaluation_points=iq.evaluation_points or [],
                model_answer_structure=iq.model_answer_structure or "",
            )
        )

    cat_schemas = [
        InterviewCategorySchema(
            category_name=cat_name,
            questions=cat_dict[cat_name],
        )
        for cat_name in cat_dict
    ]

    target_role_str = role_name or "GenAI Engineer"
    total_q = sum(len(c.questions) for c in cat_schemas)

    return InterviewPreparationResponse(
        candidate_id=candidate_id,
        target_role=target_role_str,
        total_questions=total_q,
        categories=cat_schemas,
    )
