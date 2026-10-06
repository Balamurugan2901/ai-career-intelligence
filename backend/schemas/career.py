from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CareerPathBase(BaseModel):
    """Schema representing a single matched career path."""
    role_name: str = Field(description="Target role title e.g. GenAI Engineer")
    fit_score: float = Field(description="Heuristic Profile Fit Score (0.0 to 100.0)")
    reasoning: str = Field(description="Structured rationale for why candidate matches or lacks fit")
    matching_skills: List[str] = Field(default_factory=list, description="Candidate skills matching role requirements")
    missing_skills: List[str] = Field(default_factory=list, description="Required skills missing from candidate profile")
    recommended_next_step: str = Field(description="Specific actionable advice to close skill gap for this role")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved RAG knowledge sources")


class CareerMatchListResponse(BaseModel):
    """API response model for POST /career/match and GET /career/matches."""
    candidate_id: int
    candidate_name: Optional[str] = None
    total_matches: int
    career_paths: List[CareerPathBase]
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved RAG knowledge sources")

