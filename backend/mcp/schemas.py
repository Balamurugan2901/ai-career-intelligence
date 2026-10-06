from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# MCP Protocol Models
# ---------------------------------------------------------------------------

class MCPToolDefinition(BaseModel):
    """MCP Tool Metadata & Schema Definition."""
    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Human-readable summary of tool capabilities")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="JSON Schema of expected parameters")


class MCPToolCall(BaseModel):
    """MCP Tool Execution Request Payload."""
    name: str = Field(..., description="Name of tool to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Key-value arguments for tool execution")


class MCPToolResult(BaseModel):
    """Standardized MCP Tool Execution Output Response."""
    tool_name: str = Field(..., description="Name of tool executed")
    success: bool = Field(..., description="Execution status boolean")
    data: Optional[Any] = Field(default=None, description="Returned payload object if successful")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    source: str = Field(default="MCP Local Reference Provider", description="Provenance tracking identifier")


# ---------------------------------------------------------------------------
# Tool 1: Role Requirements
# ---------------------------------------------------------------------------

class RoleRequirementsQuery(BaseModel):
    """Input parameters for get_role_requirements tool."""
    role_name: str = Field(..., description="Target role name e.g. GenAI Engineer, AI Engineer, Data Scientist")


class RoleRequirementsResult(BaseModel):
    """Output model for get_role_requirements tool."""
    role_name: str
    role_title: str
    summary: str
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    source: str = Field(default="MCP Local Reference Provider")


# ---------------------------------------------------------------------------
# Tool 2: Job Search
# ---------------------------------------------------------------------------

class JobSearchQuery(BaseModel):
    """Input parameters for search_jobs tool."""
    keyword: str = Field(..., description="Keyword search term e.g. Python, RAG, SQL, Docker")
    role_name: Optional[str] = Field(default=None, description="Optional target role filter")


class JobSearchResult(BaseModel):
    """Output model for search_jobs tool."""
    keyword: str
    total_matches: int
    matches: List[Dict[str, Any]] = Field(default_factory=list)
    source: str = Field(default="MCP Local Reference Provider")


# ---------------------------------------------------------------------------
# Tool 3: Market Benchmark
# ---------------------------------------------------------------------------

class MarketBenchmarkQuery(BaseModel):
    """Input parameters for get_market_benchmark tool."""
    role_name: str = Field(..., description="Target career role name e.g. GenAI Engineer")


class MarketBenchmarkResult(BaseModel):
    """Output model for get_market_benchmark tool."""
    role_name: str
    demand_level: str
    top_required_skills: List[str] = Field(default_factory=list)
    emerging_skills: List[str] = Field(default_factory=list)
    tools_and_frameworks: List[str] = Field(default_factory=list)
    cloud_technologies: List[str] = Field(default_factory=list)
    key_responsibilities: List[str] = Field(default_factory=list)
    salary_trend_summary: str
    data_source: str = Field(default="MCP Local Reference Provider")


# ---------------------------------------------------------------------------
# Tool 4: Skill Dependencies
# ---------------------------------------------------------------------------

class SkillDependencyQuery(BaseModel):
    """Input parameters for search_skill_dependencies tool."""
    skill_name: str = Field(..., description="Target technical skill e.g. PyTorch, RAG, SQL, Python")


class SkillDependencyResult(BaseModel):
    """Output model for search_skill_dependencies tool."""
    skill_name: str
    canonical_skill: str
    prerequisites: List[str] = Field(default_factory=list)
    core_topics: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    description: str
    source: str = Field(default="MCP Local Reference Provider")


# ---------------------------------------------------------------------------
# Tool 5: Learning Resources
# ---------------------------------------------------------------------------

class LearningResourcesQuery(BaseModel):
    """Input parameters for search_learning_resources tool."""
    skill_name: str = Field(..., description="Target skill or topic e.g. RAG, FastAPI, Python")


class LearningResourcesResult(BaseModel):
    """Output model for search_learning_resources tool."""
    skill_name: str
    total_found: int
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    source: str = Field(default="MCP Local Reference Provider")


# ---------------------------------------------------------------------------
# Tool 6: Interview Questions Bank
# ---------------------------------------------------------------------------

class InterviewQuestionsQuery(BaseModel):
    """Input parameters for search_interview_bank tool."""
    category: Optional[str] = Field(default=None, description="Optional question category filter")
    role_name: Optional[str] = Field(default=None, description="Optional target role filter")


class InterviewQuestionsResult(BaseModel):
    """Output model for search_interview_bank tool."""
    category: str
    total_questions: int
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    source: str = Field(default="MCP Local Reference Provider")
