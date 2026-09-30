from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.agents.project_agent import project_agent
from backend.agents.skill_gap_agent import skill_gap_agent
from backend.models.database import get_db
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.project_repository import ProjectRepository
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.projects import ProjectItemSchema, ProjectRecommendationResponse
from backend.utils.logger import logger

router = APIRouter(prefix="/projects", tags=["Project Recommendations"])


@router.post("/recommend/{candidate_id}", response_model=ProjectRecommendationResponse)
def generate_project_recommendations(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Target career role name"),
    db: Session = Depends(get_db),
):
    """
    Generates 3 tailored portfolio projects (Beginner, Intermediate, Advanced)
    specifically designed to close candidate skill gaps, persists in DB, and returns response.
    """
    logger.info(f"Generating project recommendations for Candidate #{candidate_id}...")

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

    # Recommend Projects
    recommendations_res = project_agent.recommend_projects(
        profile=profile_schema,
        target_role=role_name,
        skill_gaps=gap_response.gaps,
        candidate_id=candidate_id,
    )

    # Persist to Database
    ProjectRepository.save_project_recommendations(db, candidate_id, recommendations_res.projects)

    return recommendations_res


@router.get("/{candidate_id}", response_model=ProjectRecommendationResponse)
def get_candidate_project_recommendations(
    candidate_id: int,
    role_name: Optional[str] = Query(default=None, description="Filter target role name"),
    db: Session = Depends(get_db),
):
    """Retrieves saved project recommendations for a candidate profile."""
    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    db_projects = ProjectRepository.get_project_recommendations_by_candidate_id(db, candidate_id)
    if not db_projects:
        # Fallback to generating recommendations if not yet stored
        paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
        target_role_str = role_name or (paths[0].role_name if paths else "GenAI Engineer")
        return generate_project_recommendations(candidate_id, role_name=target_role_str, db=db)

    project_schemas = [
        ProjectItemSchema(
            project_title=p.project_title,
            difficulty=p.difficulty or "Intermediate",
            problem_statement=p.problem_statement or "",
            why_this_project=p.why_this_project or "",
            skills_covered=p.skills_covered or [],
            expected_features=p.expected_features or [],
            technology_stack=p.technology_stack or [],
            learning_outcomes=p.learning_outcomes or [],
            resume_value=p.resume_value or "",
            suggested_extensions=p.suggested_extensions or [],
        )
        for p in db_projects
    ]

    target_role_str = role_name or "GenAI Engineer"

    return ProjectRecommendationResponse(
        candidate_id=candidate_id,
        target_role=target_role_str,
        total_projects=len(project_schemas),
        projects=project_schemas,
    )
