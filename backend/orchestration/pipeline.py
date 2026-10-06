import datetime
import time
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from backend.agents.resume_agent import resume_agent
from backend.agents.career_agent import career_agent
from backend.agents.market_agent import market_agent
from backend.agents.skill_gap_agent import skill_gap_agent
from backend.agents.roadmap_agent import roadmap_agent
from backend.agents.project_agent import project_agent
from backend.agents.interview_agent import interview_agent

from backend.models.interview import AnalysisRun
from backend.orchestration.cache import pipeline_cache
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository
from backend.repositories.market_repository import MarketRepository
from backend.repositories.skill_gap_repository import SkillGapRepository
from backend.repositories.roadmap_repository import RoadmapRepository
from backend.repositories.project_repository import ProjectRepository
from backend.repositories.interview_repository import InterviewRepository

from backend.schemas.analysis import FullAnalysisSummaryResponse
from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.career import CareerPathBase
from backend.schemas.market import MarketRoleDemand
from backend.schemas.skill_gap import SkillGapAnalysisResponse, SkillGapItem
from backend.schemas.roadmap import LearningRoadmapResponse
from backend.schemas.projects import ProjectRecommendationResponse
from backend.schemas.interview import InterviewPreparationResponse
from backend.utils.logger import logger


class CareerAnalysisPipeline:
    """
    Orchestration Engine for AI Career Intelligence Platform.
    Executes all 7 independent AI agents in strict managed sequence with RAG evidence,
    MCP tool coordination, intelligent caching, and granular stage status logging.
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

    STAGES = [
        "PARSING_RESUME",
        "MATCHING_CAREERS",
        "ANALYZING_MARKET",
        "EVALUATING_SKILL_GAPS",
        "GENERATING_ROADMAP",
        "RECOMMENDING_PROJECTS",
        "PREPARING_INTERVIEWS",
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
        Executes the full end-to-end multi-agent pipeline workflow with caching and stage status updates.
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
                status="PENDING",
                agents_completed=[],
                created_at=datetime.datetime.now(datetime.timezone.utc),
            )
            db.add(run_rec)
            db.flush()

        completed_agents: List[str] = []

        try:
            # Stage 1: Resume Intelligence Agent
            logger.info(f"--- Stage 1: {cls.AGENT_NAMES[0]} ({cls.STAGES[0]}) ---")
            cls._update_run_status(db, run_rec, cls.STAGES[0], completed_agents)
            if profile_record.profile_json:
                profile_schema = CandidateProfileSchema.model_validate(profile_record.profile_json)
            else:
                profile_schema = resume_agent.analyze_resume(profile_record.resume.raw_text)

            completed_agents.append(cls.AGENT_NAMES[0])

            # Stage 2: Career Matching Agent
            logger.info(f"--- Stage 2: {cls.AGENT_NAMES[1]} ({cls.STAGES[1]}) ---")
            cls._update_run_status(db, run_rec, cls.STAGES[1], completed_agents)
            matched_paths = career_agent.match_career_paths(profile_schema, candidate_id=candidate_id, top_n=5)
            CareerRepository.save_career_paths(db, candidate_id, matched_paths)
            completed_agents.append(cls.AGENT_NAMES[1])

            selected_role = target_role or (matched_paths[0].role_name if matched_paths else "GenAI Engineer")

            # Check Pipeline Cache after profile & target_role resolution
            cache_key = pipeline_cache.generate_key(
                candidate_id=candidate_id,
                target_role=selected_role,
                profile_summary=profile_schema.professional_summary,
                skills=profile_schema.skills.all_skills_list(),
            )
            cached_data = pipeline_cache.get(cache_key)

            if cached_data:
                logger.info(f"Cache HIT: Returning cached pipeline response for Candidate #{candidate_id} ({selected_role}).")
                cached_res = FullAnalysisSummaryResponse.model_validate(cached_data)
                cached_res.cached = True
                cached_res.analysis_id = run_rec.id

                elapsed = round(time.time() - start_time, 2)
                run_rec.status = "COMPLETED"
                run_rec.execution_time_seconds = elapsed
                run_rec.agents_completed = cls.AGENT_NAMES
                run_rec.completed_at = datetime.datetime.now(datetime.timezone.utc)
                db.commit()
                return cached_res


            # Stage 3: Market Intelligence Agent
            logger.info(f"--- Stage 3: {cls.AGENT_NAMES[2]} ({cls.STAGES[2]}) ---")
            cls._update_run_status(db, run_rec, cls.STAGES[2], completed_agents)
            role_names = [p.role_name for p in matched_paths] if matched_paths else [selected_role]
            market_demands = market_agent.analyze_market_for_roles(role_names)
            db_paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
            if db_paths:
                MarketRepository.save_market_requirements_for_career_paths(db, db_paths, market_demands)
            completed_agents.append(cls.AGENT_NAMES[2])

            # Stage 4: Skill Gap Agent
            logger.info(f"--- Stage 4: {cls.AGENT_NAMES[3]} ({cls.STAGES[3]}) ---")
            cls._update_run_status(db, run_rec, cls.STAGES[3], completed_agents)
            gap_analysis = skill_gap_agent.analyze_candidate_gaps(
                profile=profile_schema,
                target_role=selected_role,
                candidate_id=candidate_id,
            )
            SkillGapRepository.save_skill_gaps(db, candidate_id, selected_role, gap_analysis.gaps)
            completed_agents.append(cls.AGENT_NAMES[3])

            # Stage 5: Learning Roadmap Agent
            logger.info(f"--- Stage 5: {cls.AGENT_NAMES[4]} ({cls.STAGES[4]}) ---")
            cls._update_run_status(db, run_rec, cls.STAGES[4], completed_agents)
            roadmap = roadmap_agent.generate_roadmap(
                profile=profile_schema,
                target_role=selected_role,
                skill_gaps=gap_analysis.gaps,
                candidate_id=candidate_id,
            )
            roadmap_db = RoadmapRepository.save_roadmap(db, candidate_id, selected_role, roadmap)
            roadmap.roadmap_id = roadmap_db.id
            completed_agents.append(cls.AGENT_NAMES[4])

            # Stage 6: Project Recommendation Agent
            logger.info(f"--- Stage 6: {cls.AGENT_NAMES[5]} ({cls.STAGES[5]}) ---")
            cls._update_run_status(db, run_rec, cls.STAGES[5], completed_agents)
            project_recs = project_agent.recommend_projects(
                profile=profile_schema,
                target_role=selected_role,
                skill_gaps=gap_analysis.gaps,
                candidate_id=candidate_id,
            )
            ProjectRepository.save_project_recommendations(db, candidate_id, project_recs.projects)
            completed_agents.append(cls.AGENT_NAMES[5])

            # Stage 7: Interview Preparation Agent
            logger.info(f"--- Stage 7: {cls.AGENT_NAMES[6]} ({cls.STAGES[6]}) ---")
            cls._update_run_status(db, run_rec, cls.STAGES[6], completed_agents)
            interview_prep = interview_agent.generate_interview_prep(
                profile=profile_schema,
                target_role=selected_role,
                skill_gaps=gap_analysis.gaps,
                candidate_id=candidate_id,
            )
            InterviewRepository.save_interview_questions(db, candidate_id, interview_prep.categories)
            completed_agents.append(cls.AGENT_NAMES[6])

            # Aggregate Evidence Sources across all agents
            evidence_sources = cls._collect_evidence_sources(
                matched_paths, market_demands, gap_analysis, roadmap, project_recs, interview_prep
            )

            # Finalize Status & Metrics
            elapsed = round(time.time() - start_time, 2)

            run_rec.status = "COMPLETED"
            run_rec.execution_time_seconds = elapsed
            run_rec.agents_completed = completed_agents
            run_rec.completed_at = datetime.datetime.now(datetime.timezone.utc)
            db.commit()

            response = FullAnalysisSummaryResponse(
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
                cached=False,
                evidence_sources=evidence_sources,
            )

            # Store in cache for future instant hits
            pipeline_cache.set(cache_key, response.model_dump())

            logger.info(f"CareerAnalysisPipeline completed in {elapsed}s for Candidate #{candidate_id}.")
            return response

        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            logger.error(f"Critical CareerAnalysisPipeline error for Candidate #{candidate_id}: {e}", exc_info=True)
            run_rec.status = "FAILED"
            run_rec.error_message = str(e)
            run_rec.execution_time_seconds = elapsed
            run_rec.agents_completed = completed_agents
            db.commit()
            raise e


    @classmethod
    def _collect_evidence_sources(
        cls,
        career_matches: List[CareerPathBase],
        market_demands: List[MarketRoleDemand],
        gap_analysis: SkillGapAnalysisResponse,
        roadmap: LearningRoadmapResponse,
        project_recs: ProjectRecommendationResponse,
        interview_prep: InterviewPreparationResponse,
    ) -> List[Dict[str, Any]]:
        """Collects and deduplicates RAG document sources and MCP tool provenance across all agent outputs."""
        raw_list = []

        for cm in career_matches:
            raw_list.extend(getattr(cm, "sources", []) or [])

        for md in market_demands:
            raw_list.extend(getattr(md, "sources", []) or [])

        raw_list.extend(getattr(gap_analysis, "sources", []) or [])
        raw_list.extend(getattr(roadmap, "sources", []) or [])
        raw_list.extend(getattr(project_recs, "sources", []) or [])
        raw_list.extend(getattr(interview_prep, "sources", []) or [])

        deduped = []
        seen = set()
        for item in raw_list:
            if isinstance(item, dict):
                key = item.get("title") or item.get("source") or str(item)
            else:
                key = str(item)
            if key not in seen:
                seen.add(key)
                deduped.append(item if isinstance(item, dict) else {"source": str(item)})

        return deduped

    @classmethod
    def _update_run_status(cls, db: Session, run_rec: AnalysisRun, status_str: str, agents: List[str]):
        """Helper to update intermediate pipeline run state in database."""
        run_rec.status = status_str
        run_rec.agents_completed = list(agents)
        db.commit()


pipeline_orchestrator = CareerAnalysisPipeline()

