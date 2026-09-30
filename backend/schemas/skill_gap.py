from typing import List, Optional
from pydantic import BaseModel, Field


class SkillGapItem(BaseModel):
    """Structured representation of a single identified skill gap or strength."""
    skill: str = Field(description="Normalized canonical skill name e.g. LangChain")
    current_level: str = Field(default="None", description="Current level: None, Beginner, Intermediate, Advanced")
    target_level: str = Field(default="Intermediate", description="Required level: Intermediate, Advanced, Expert")
    priority: str = Field(default="MEDIUM", description="Priority level: HIGH, MEDIUM, LOW")
    gap_type: str = Field(default="missing", description="Classification: missing, partial, strength, outdated")
    reason: str = Field(description="Clear explanation of why this skill gap exists and why it matters for target role")
    estimated_learning_effort: str = Field(default="2-3 weeks", description="Estimated effort e.g. 1-2 weeks")
    dependency_skills: List[str] = Field(default_factory=list, description="Prerequisite skills required before learning this skill")


class SkillGapAnalysisResponse(BaseModel):
    """API response model for POST /skill-gap/analyze and GET /skill-gap/{candidate_id}."""
    candidate_id: int
    target_role: str
    total_gaps: int
    high_priority_count: int
    medium_priority_count: int
    matched_strengths_count: int
    gaps: List[SkillGapItem]
