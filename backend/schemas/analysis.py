from typing import List, Optional
from pydantic import BaseModel, Field

from backend.schemas.candidate import CandidateProfileSchema
from backend.schemas.career import CareerPathBase
from backend.schemas.market import MarketRoleDemand
from backend.schemas.skill_gap import SkillGapAnalysisResponse
from backend.schemas.roadmap import LearningRoadmapResponse
from backend.schemas.projects import ProjectRecommendationResponse
from backend.schemas.interview import InterviewPreparationResponse


class AnalysisStartRequest(BaseModel):
    """Payload model for starting end-to-end multi-agent career analysis pipeline."""
    candidate_id: int = Field(description="Candidate profile ID")
    target_role: Optional[str] = Field(default=None, description="Optional target role override; defaults to top heuristic career match")


class AnalysisStatusResponse(BaseModel):
    """Execution status for a pipeline analysis run."""
    analysis_id: int
    candidate_id: int
    resume_id: int
    status: str = Field(description="Status: PENDING, RUNNING, COMPLETED, FAILED")
    execution_time_seconds: Optional[float] = None
    agents_completed: List[str] = Field(default_factory=list, description="Names of completed pipeline agents")
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class FullAnalysisSummaryResponse(BaseModel):
    """Aggregated full career intelligence package combining all 7 agents' outputs."""
    analysis_id: int
    candidate_id: int
    target_role: str
    execution_time_seconds: Optional[float] = None
    profile: CandidateProfileSchema
    career_matches: List[CareerPathBase]
    market_intelligence: List[MarketRoleDemand]
    skill_gap_analysis: SkillGapAnalysisResponse
    learning_roadmap: LearningRoadmapResponse
    project_recommendations: ProjectRecommendationResponse
    interview_preparation: InterviewPreparationResponse
