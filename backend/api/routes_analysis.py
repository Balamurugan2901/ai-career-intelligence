from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.orchestration.pipeline import CareerAnalysisPipeline
from backend.repositories.analysis_repository import AnalysisRepository
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.market_repository import MarketRepository
from backend.repositories.skill_gap_repository import SkillGapRepository
from backend.repositories.roadmap_repository import RoadmapRepository
from backend.repositories.project_repository import ProjectRepository
from backend.repositories.interview_repository import InterviewRepository

from backend.agents.market_agent import market_agent
from backend.agents.skill_gap_agent import skill_gap_agent
from backend.agents.roadmap_agent import roadmap_agent
from backend.agents.project_agent import project_agent
from backend.agents.interview_agent import interview_agent

from backend.schemas.analysis import (
    AnalysisStartRequest,
    AnalysisStatusResponse,
    FullAnalysisSummaryResponse,
)
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.career import CareerPathBase
from backend.schemas.roadmap import RoadmapPhaseSchema, RoadmapItemSchema
from backend.schemas.projects import ProjectItemSchema
from backend.schemas.interview import InterviewCategorySchema, InterviewQuestionItemSchema
from backend.utils.logger import logger

router = APIRouter(prefix="/analysis", tags=["Pipeline Analysis"])


@router.post("/start", response_model=AnalysisStatusResponse)
def start_pipeline_analysis(
    request: AnalysisStartRequest,
    db: Session = Depends(get_db),
):
    """
    Triggers the end-to-end multi-agent career analysis pipeline for a candidate.
    Orchestrates all 7 agents in sequence, updates execution run status, and returns run status.
    """
    logger.info(f"Received request to start analysis pipeline for Candidate #{request.candidate_id}")

    profile_record = CandidateRepository.get_profile_by_id(db, request.candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{request.candidate_id} not found.",
        )

    try:
        summary_res = CareerAnalysisPipeline.execute(
            db=db,
            candidate_id=request.candidate_id,
            target_role=request.target_role,
        )

        run_rec = AnalysisRepository.get_analysis_run_by_id(db, summary_res.analysis_id)
        if not run_rec:
            raise HTTPException(status_code=500, detail="Failed to retrieve execution record.")

        return AnalysisStatusResponse(
            analysis_id=run_rec.id,
            candidate_id=request.candidate_id,
            resume_id=run_rec.resume_id,
            status=run_rec.status,
            execution_time_seconds=run_rec.execution_time_seconds,
            agents_completed=run_rec.agents_completed or [],
            created_at=run_rec.created_at.isoformat() if run_rec.created_at else None,
            completed_at=run_rec.completed_at.isoformat() if run_rec.completed_at else None,
        )

    except Exception as e:
        logger.error(f"Error starting analysis pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline execution error: {str(e)}",
        )


@router.get("/{analysis_id}", response_model=AnalysisStatusResponse)
def get_analysis_status(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves current execution status of a pipeline run by analysis ID."""
    run_rec = AnalysisRepository.get_analysis_run_by_id(db, analysis_id)
    if not run_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis run #{analysis_id} not found.",
        )

    profile = CandidateRepository.get_profile_by_id(db, run_rec.resume.profile.id) if run_rec.resume and run_rec.resume.profile else None

    return AnalysisStatusResponse(
        analysis_id=run_rec.id,
        candidate_id=profile.id if profile else 1,
        resume_id=run_rec.resume_id,
        status=run_rec.status,
        execution_time_seconds=run_rec.execution_time_seconds,
        agents_completed=run_rec.agents_completed or [],
        error_message=run_rec.error_message,
        created_at=run_rec.created_at.isoformat() if run_rec.created_at else None,
        completed_at=run_rec.completed_at.isoformat() if run_rec.completed_at else None,
    )


@router.get("/candidate/{candidate_id}/full", response_model=FullAnalysisSummaryResponse)
def get_full_candidate_analysis_summary(
    candidate_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves full aggregated 7-agent career intelligence summary for a candidate profile."""
    profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
    if not profile_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate profile #{candidate_id} not found.",
        )

    # 1. Profile
    if profile_record.profile_json:
        profile_schema = CandidateProfileSchema.model_validate(profile_record.profile_json)
    else:
        profile_schema = CandidateProfileSchema(
            name=profile_record.name or "Candidate",
            professional_summary=profile_record.professional_summary or "",
            years_of_experience=profile_record.years_of_experience or 0.0,
        )

    # 2. Career Matches
    db_paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
    if not db_paths:
        # Run pipeline if not yet analyzed
        return CareerAnalysisPipeline.execute(db=db, candidate_id=candidate_id)

    career_matches = [
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

    selected_role = career_matches[0].role_name if career_matches else "GenAI Engineer"

    # 3. Market Intelligence
    role_names = [p.role_name for p in career_matches]
    market_intelligence = market_agent.analyze_market_for_roles(role_names)

    # 4. Skill Gap Analysis
    gap_analysis = skill_gap_agent.analyze_candidate_gaps(profile_schema, selected_role, candidate_id)

    # 5. Learning Roadmap
    roadmap = roadmap_agent.generate_roadmap(profile_schema, selected_role, gap_analysis.gaps, candidate_id)

    # 6. Project Recommendations
    projects = project_agent.recommend_projects(profile_schema, selected_role, gap_analysis.gaps, candidate_id)

    # 7. Interview Preparation
    interview_prep = interview_agent.generate_interview_prep(profile_schema, selected_role, gap_analysis.gaps, candidate_id)

    latest_run = AnalysisRepository.get_latest_run_for_candidate(db, candidate_id)

    return FullAnalysisSummaryResponse(
        analysis_id=latest_run.id if latest_run else 1,
        candidate_id=candidate_id,
        target_role=selected_role,
        execution_time_seconds=latest_run.execution_time_seconds if latest_run else 1.5,
        profile=profile_schema,
        career_matches=career_matches,
        market_intelligence=market_intelligence,
        skill_gap_analysis=gap_analysis,
        learning_roadmap=roadmap,
        project_recommendations=projects,
        interview_preparation=interview_prep,
    )
