from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectItemSchema(BaseModel):
    """Structured representation of a recommended portfolio project."""
    project_title: str = Field(description="Project title e.g. Production RAG Knowledge Base System")
    difficulty: str = Field(default="Intermediate", description="Level: Beginner, Intermediate, Advanced")
    problem_statement: str = Field(description="Real-world problem or business need addressed by this project")
    why_this_project: str = Field(description="Explicit rationale connecting project to candidate's identified skill gaps")
    skills_covered: List[str] = Field(default_factory=list, description="Target skills taught and demonstrated by project")
    expected_features: List[str] = Field(default_factory=list, description="Core technical capabilities to implement")
    technology_stack: List[str] = Field(default_factory=list, description="Frameworks, tools, databases, and APIs used")
    learning_outcomes: List[str] = Field(default_factory=list, description="Key skills and knowledge candidate gains upon completion")
    resume_value: str = Field(description="How to phrase and highlight this project on a resume or in interviews")
    suggested_extensions: List[str] = Field(default_factory=list, description="Advanced next-level features to make project stand out")


class ProjectRecommendationResponse(BaseModel):
    """API response model for POST /projects/recommend and GET /projects/{candidate_id}."""
    candidate_id: int
    target_role: str
    total_projects: int
    projects: List[ProjectItemSchema]
