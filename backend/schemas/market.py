from typing import List, Optional
from pydantic import BaseModel, Field


class MarketRoleDemand(BaseModel):
    """Structured market demand representation for a single career role."""
    role_name: str = Field(description="Role title e.g. GenAI Engineer")
    demand_level: str = Field(default="HIGH DEMAND", description="Categorization: HIGH DEMAND, MEDIUM DEMAND, LOWER PRIORITY")
    top_required_skills: List[str] = Field(default_factory=list, description="Core required skills in active demand")
    emerging_skills: List[str] = Field(default_factory=list, description="Rapidly growing skills in market demand")
    tools_and_frameworks: List[str] = Field(default_factory=list, description="Key frameworks and developer tooling")
    cloud_technologies: List[str] = Field(default_factory=list, description="Cloud infrastructure and DevOps tech")
    key_responsibilities: List[str] = Field(default_factory=list, description="Common market job responsibilities")
    salary_trend_summary: Optional[str] = Field(default=None, description="Qualitative summary of compensation trends")
    data_source: str = Field(default="Market insight based on configured reference data", description="Source provenance metadata")
    updated_at: Optional[str] = Field(default=None, description="ISO timestamp of reference update")


class MarketIntelligenceResponse(BaseModel):
    """API response model for POST /market/analyze/{candidate_id}."""
    candidate_id: int
    analyzed_roles_count: int
    market_demands: List[MarketRoleDemand]
