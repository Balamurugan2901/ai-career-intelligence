from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.agents.roadmap_agent import roadmap_agent
from backend.agents.skill_gap_agent import skill_gap_agent
from backend.models.database import get_db
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.roadmap_repository import RoadmapRepository
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.roadmap import (
    LearningRoadmapResponse,
    RoadmapPhaseSchema,
    RoadmapItemSchema,
)
from backend.utils.logger import logger

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmap"])


@router.post("/generate/{candidate_id}", response_model=LearningRoadmapResponse)
def generate_learning_roadmap(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Target career role name"),
    db: Session = Depends(get_db),
):
    """
    Generates a personalized 6-phase learning roadmap for a candidate profile.
    Sequences foundational prerequisites before advanced GenAI specialization tools,
    persists roadmap to SQLite DB, and returns structured action plan.
    """
    logger.info(f"Generating learning roadmap for Candidate #{candidate_id}...")

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

    # Generate Learning Roadmap
    roadmap_res = roadmap_agent.generate_roadmap(
        profile=profile_schema,
        target_role=role_name,
        skill_gaps=gap_response.gaps,
        candidate_id=candidate_id,
    )

    # Persist to Database
    roadmap_db = RoadmapRepository.save_roadmap(db, candidate_id, role_name, roadmap_res)
    roadmap_res.roadmap_id = roadmap_db.id

    return roadmap_res


@router.get("/{candidate_id}", response_model=LearningRoadmapResponse)
def get_candidate_roadmap(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Filter by target role name"),
    db: Session = Depends(get_db),
):
    """Retrieves saved active learning roadmap for a candidate profile."""
    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    roadmap_db = RoadmapRepository.get_roadmap_by_candidate_id(db, candidate_id, target_role=role_name)
    if not roadmap_db:
        # Fallback to generating roadmap if not yet stored
        paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
        target_role_str = role_name or (paths[0].role_name if paths else "GenAI Engineer")
        return generate_learning_roadmap(candidate_id, role_name=target_role_str, db=db)

    # Group items by phase
    phase_dict: dict[int, list[RoadmapItemSchema]] = {}
    phase_names_dict: dict[int, str] = {}

    for item in roadmap_db.items:
        p_num = item.phase_number
        if p_num not in phase_dict:
            phase_dict[p_num] = []
            phase_names_dict[p_num] = item.phase_name or f"Phase {p_num}"

        phase_dict[p_num].append(
            RoadmapItemSchema(
                skill=item.skill_name,
                why_it_matters=item.why_it_matters or "",
                what_to_learn=item.what_to_learn or "",
                prerequisites=item.prerequisites or [],
                practical_task=item.practical_task or "",
                mini_project=item.mini_project or "",
                validation_method=item.validation_method or "",
                estimated_effort=item.estimated_effort or "10 hours",
            )
        )

    phase_schemas = [
        RoadmapPhaseSchema(
            phase_number=p_num,
            phase_name=phase_names_dict[p_num],
            items=phase_dict[p_num],
        )
        for p_num in sorted(phase_dict.keys())
    ]

    return LearningRoadmapResponse(
        roadmap_id=roadmap_db.id,
        candidate_id=candidate_id,
        target_role=roadmap_db.target_role,
        total_phases=len(phase_schemas),
        total_estimated_hours="115 hours",
        phases=phase_schemas,
    )
