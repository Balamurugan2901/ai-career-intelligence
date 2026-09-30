from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.agents.career_agent import career_agent
from backend.models.database import get_db
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.career import CareerPathBase, CareerMatchListResponse
from backend.utils.logger import logger

router = APIRouter(prefix="/career", tags=["Career Matching"])


@router.post("/match/{candidate_id}", response_model=CareerMatchListResponse)
def generate_career_matches(
    candidate_id: int,
    top_n: int = 5,
    db: Session = Depends(get_db),
):
    """
    Triggers career matching analysis for candidate profile.
    Calculates deterministic heuristic scores, enriches with GenAI reasoning,
    persists results to SQLite DB, and returns ranked matches.
    """
    logger.info(f"Generating career matches for Candidate #{candidate_id}...")

    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    # Reconstruct CandidateProfileSchema from profile_json or record fields
    if profile_record.profile_json:
        profile_schema = CandidateProfileSchema.model_validate(profile_record.profile_json)
    else:
        profile_schema = CandidateProfileSchema(
            name=profile_record.name or "Candidate",
            professional_summary=profile_record.professional_summary or "",
            years_of_experience=profile_record.years_of_experience or 0.0,
        )

    # Run CareerMatchingAgent
    matched_paths: list[CareerPathBase] = career_agent.match_career_paths(
        profile=profile_schema,
        candidate_id=candidate_id,
        top_n=top_n,
    )

    # Persist matches to Database
    CareerRepository.save_career_paths(db, candidate_id, matched_paths)

    return CareerMatchListResponse(
        candidate_id=candidate_id,
        candidate_name=profile_record.name,
        total_matches=len(matched_paths),
        career_paths=matched_paths,
    )


@router.get("/matches/{candidate_id}", response_model=CareerMatchListResponse)
def get_career_matches(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves saved career path matches for a candidate profile."""
    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    db_paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
    
    path_schemas = [
        CareerPathBase(
            role_name=p.role_name,
            fit_score=p.fit_score,
            reasoning=p.reasoning or "",
            matching_skills=p.matching_skills or [],
            missing_skills=p.missing_skills or [],
            recommended_next_step=p.recommended_next_step or "",
        )
        for p in db_paths
    ]

    return CareerMatchListResponse(
        candidate_id=candidate_id,
        candidate_name=profile_record.name,
        total_matches=len(path_schemas),
        career_paths=path_schemas,
    )
