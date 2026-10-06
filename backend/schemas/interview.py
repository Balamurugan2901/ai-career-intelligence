from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InterviewQuestionItemSchema(BaseModel):
    """Structured representation of a single interview preparation question."""
    question: str = Field(description="Clear, conceptual interview question")
    category: str = Field(description="Category: Resume Questions, Project Questions, Technical Questions, Coding Questions, AI/ML Questions, GenAI Questions, Behavioral Questions, HR Questions")
    difficulty: str = Field(default="Mid-Level", description="Difficulty: Junior, Mid-Level, Senior")
    expected_concepts: List[str] = Field(default_factory=list, description="Core technical concepts evaluated by question")
    evaluation_points: List[str] = Field(default_factory=list, description="Bullet points of what constitutes a strong candidate response")
    model_answer_structure: str = Field(description="Step-by-step structural framework for answering, avoiding rote scripts")


class InterviewCategorySchema(BaseModel):
    """Categorized group of interview questions."""
    category_name: str = Field(description="Category name e.g. GenAI Questions")
    questions: List[InterviewQuestionItemSchema] = Field(default_factory=list, description="Questions in this category")


class InterviewPreparationResponse(BaseModel):
    """API response model for POST /interview/generate and GET /interview/{candidate_id}."""
    candidate_id: int
    target_role: str
    total_questions: int
    categories: List[InterviewCategorySchema]
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Retrieved RAG knowledge sources")

