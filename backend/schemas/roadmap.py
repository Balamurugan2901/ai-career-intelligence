from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RoadmapItemSchema(BaseModel):
    """Structured learning item within a roadmap phase."""
    skill: str = Field(description="Skill name to master e.g. LangChain")
    why_it_matters: str = Field(description="Clear explanation of why this skill is vital for the target role")
    what_to_learn: str = Field(description="Specific concepts, modules, and API surfaces to study")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite skills required before starting")
    practical_task: str = Field(description="Hands-on coding exercise or practical task")
    mini_project: str = Field(description="Deliverable mini-project to build and demonstrate mastery")
    validation_method: str = Field(description="How to verify mastery e.g. Pass test suite, deploy API")
    estimated_effort: str = Field(default="10 hours", description="Estimated learning time e.g. 10 hours")


class RoadmapPhaseSchema(BaseModel):
    """Structured roadmap phase grouping multiple learning items."""
    phase_number: int = Field(description="Phase sequence number (1 to 6)")
    phase_name: str = Field(description="Phase title e.g. Phase 1: Foundations")
    items: List[RoadmapItemSchema] = Field(default_factory=list, description="Learning items in this phase")


class LearningRoadmapResponse(BaseModel):
    """API response model for POST /roadmap/generate and GET /roadmap/{candidate_id}."""
    roadmap_id: Optional[int] = None
    candidate_id: int
    target_role: str
    total_phases: int
    total_estimated_hours: str
    phases: List[RoadmapPhaseSchema]
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved RAG knowledge sources")

