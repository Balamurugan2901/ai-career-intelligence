import datetime
import time
from typing import Optional, List
from sqlalchemy.orm import Session

from backend.agents.resume_agent import resume_agent
from backend.agents.career_agent import career_agent
from backend.agents.market_agent import market_agent
from backend.agents.skill_gap_agent import skill_gap_agent
from backend.agents.roadmap_agent import roadmap_agent
from backend.agents.project_agent import project_agent
from backend.agents.interview_agent import interview_agent

from backend.models.interview import AnalysisRun
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.market_repository import MarketRepository
from backend.repositories.skill_gap_repository import SkillGapRepository
from backend.repositories.roadmap_repository import RoadmapRepository
from backend.repositories.project_repository import ProjectRepository
from backend.repositories.interview_repository import InterviewRepository

from backend.schemas.analysis import FullAnalysisSummaryResponse
from backend.schemas.candidate import CandidateProfileSchema
from backend.utils.logger import logger


class CareerAnalysisPipeline:
    """
    Orchestration Engine for AI Career Intelligence Platform.
    Executes all 7 independent AI agents in strict managed sequence, passing intermediate
    structured Pydantic schemas downstream to minimize LLM token consumption and track execution state.
    """

    AGENT_NAMES = [
        "Resume Intelligence Agent",
        "Career Matching Agent",
        "Market Intelligence Agent",
        "Skill Gap Agent",
        "Learning Roadmap Agent",
        "Project Recommendation Agent",
        "Interview Preparation Agent",
    ]

    @classmethod
    def execute(
        cls,
        db: Session,
        candidate_id: int,
        target_role: Optional[str] = None,
        analysis_run_id: Optional[int] = None,
    ) -> FullAnalysisSummaryResponse:
        """
        Executes the full end-to-end multi-agent pipeline workflow.
        """
        start_time = time.time()
        logger.info(f"CareerAnalysisPipeline starting execution for Candidate #{candidate_id}...")

        # 1. Fetch Candidate Profile Record & Resume
        profile_record = CandidateRepository.get_profile_by_id(db, candidate_id)
        if not profile_record:
            raise ValueError(f"Candidate profile #{candidate_id} not found.")

        resume_id = profile_record.resume_id

        # 2. Get or initialize AnalysisRun database record
        if analysis_run_id:
            run_rec = db.query(AnalysisRun).filter(AnalysisRun.id == analysis_run_id).first()
        else:
            run_rec = AnalysisRun(
                resume_id=resume_id,
                status="RUNNING",
                agents_completed=[],
                created_at=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(run_rec)
            db.flush()

        completed_agents: List[str] = []

        try:
            # AGENT 1: Resume Intelligence Agent
            logger.info(f"--- Stage 1: {cls.AGENT_NAMES[0]} ---")
            if profile_record.profile_json:
                profile_schema = CandidateProfileSchema.model_validate(profile_record.profile_json)
            else:
                profile_schema = resume_agent.analyze_resume(profile_record.resume.raw_text)
            
            completed_agents.append(cls.AGENT_NAMES[0])
            cls._update_run_status(db, run_rec, "RUNNING", completed_agents)

            # AGENT 2: Career Matching Agent
            logger.info(f"--- Stage 2: {cls.AGENT_NAMES[1]} ---")
            matched_paths = career_agent.match_career_paths(profile_schema, candidate_id=candidate_id, top_n=5)
            CareerRepository.save_career_paths(db, candidate_id, matched_paths)
            
            completed_agents.append(cls.AGENT_NAMES[1])
            cls._update_run_status(db, run_rec, "RUNNING", completed_agents)

            # Determine primary target role
            selected_role = target_role or (matched_paths[0].role_name if matched_paths else "GenAI Engineer")

            # AGENT 3: Market Intelligence Agent
            logger.info(f"--- Stage 3: {cls.AGENT_NAMES[2]} ---")
            role_names = [p.role_name for p in matched_paths] if matched_paths else [selected_role]
            market_demands = market_agent.analyze_market_for_roles(role_names)
            
            db_paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
            if db_paths:
                MarketRepository.save_market_requirements_for_career_paths(db, db_paths, market_demands)

            completed_agents.append(cls.AGENT_NAMES[2])
            cls._update_run_status(db, run_rec, "RUNNING", completed_agents)

            # AGENT 4: Skill Gap Agent
            logger.info(f"--- Stage 4: {cls.AGENT_NAMES[3]} ---")
            gap_analysis = skill_gap_agent.analyze_candidate_gaps(
                profile=profile_schema,
                target_role=selected_role,
                candidate_id=candidate_id,
            )
            SkillGapRepository.save_skill_gaps(db, candidate_id, selected_role, gap_analysis.gaps)

            completed_agents.append(cls.AGENT_NAMES[3])
            cls._update_run_status(db, run_rec, "RUNNING", completed_agents)

            # AGENT 5: Learning Roadmap Agent
            logger.info(f"--- Stage 5: {cls.AGENT_NAMES[4]} ---")
            roadmap = roadmap_agent.generate_roadmap(
                profile=profile_schema,
                target_role=selected_role,
                skill_gaps=gap_analysis.gaps,
                candidate_id=candidate_id,
            )
            roadmap_db = RoadmapRepository.save_roadmap(db, candidate_id, selected_role, roadmap)
            roadmap.roadmap_id = roadmap_db.id

            completed_agents.append(cls.AGENT_NAMES[4])
            cls._update_run_status(db, run_rec, "RUNNING", completed_agents)

            # AGENT 6: Project Recommendation Agent
            logger.info(f"--- Stage 6: {cls.AGENT_NAMES[5]} ---")
            project_recs = project_agent.recommend_projects(
                profile=profile_schema,
                target_role=selected_role,
                skill_gaps=gap_analysis.gaps,
                candidate_id=candidate_id,
            )
            ProjectRepository.save_project_recommendations(db, candidate_id, project_recs.projects)

            completed_agents.append(cls.AGENT_NAMES[5])
            cls._update_run_status(db, run_rec, "RUNNING", completed_agents)

            # AGENT 7: Interview Preparation Agent
            logger.info(f"--- Stage 7: {cls.AGENT_NAMES[6]} ---")
            interview_prep = interview_agent.generate_interview_prep(
                profile=profile_schema,
                target_role=selected_role,
                skill_gaps=gap_analysis.gaps,
                candidate_id=candidate_id,
            )
            InterviewRepository.save_interview_questions(db, candidate_id, interview_prep.categories)

            completed_agents.append(cls.AGENT_NAMES[6])
            
            # Finalize Execution Status
            elapsed = round(time.time() - start_time, 2)
            run_rec.status = "COMPLETED"
            run_rec.execution_time_seconds = elapsed
            run_rec.agents_completed = completed_agents
            run_rec.completed_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()

            logger.info(f"CareerAnalysisPipeline finished successfully in {elapsed}s for Candidate #{candidate_id}.")

            return FullAnalysisSummaryResponse(
                analysis_id=run_rec.id,
                candidate_id=candidate_id,
                target_role=selected_role,
                execution_time_seconds=elapsed,
                profile=profile_schema,
                career_matches=matched_paths,
                market_intelligence=market_demands,
                skill_gap_analysis=gap_analysis,
                learning_roadmap=roadmap,
                project_recommendations=project_recs,
                interview_preparation=interview_prep,
            )

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"CareerAnalysisPipeline execution failed for Candidate #{candidate_id}: {e}", exc_info=True)
            run_rec.status = "FAILED"
            run_rec.error_message = str(e)
            run_rec.execution_time_seconds = elapsed
            run_rec.agents_completed = completed_agents
            db.commit()
            raise e

    @classmethod
    def _update_run_status(cls, db: Session, run_rec: AnalysisRun, status_str: str, agents: List[str]):
        """Helper to update intermediate pipeline run state in database."""
        run_rec.status = status_str
        run_rec.agents_completed = list(agents)
        db.commit()


pipeline_orchestrator = CareerAnalysisPipeline()
