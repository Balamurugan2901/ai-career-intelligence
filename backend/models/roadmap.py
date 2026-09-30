import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.models.database import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    target_role = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    profile = relationship("CandidateProfile", back_populates="roadmaps")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    phase_number = Column(Integer, nullable=False)
    phase_name = Column(String(255), nullable=False)  # e.g., Phase 1 - Foundations
    skill_name = Column(String(255), nullable=False)
    why_it_matters = Column(Text, nullable=True)
    what_to_learn = Column(Text, nullable=True)
    prerequisites = Column(JSON, nullable=True)
    practical_task = Column(Text, nullable=True)
    mini_project = Column(Text, nullable=True)
    validation_method = Column(Text, nullable=True)
    estimated_effort = Column(String(100), nullable=True)

    roadmap = relationship("Roadmap", back_populates="items")


class ProjectRecommendation(Base):
    __tablename__ = "project_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    project_title = Column(String(255), nullable=False)
    problem_statement = Column(Text, nullable=True)
    why_this_project = Column(Text, nullable=True)
    skills_covered = Column(JSON, nullable=True)
    difficulty = Column(String(50), default="Intermediate")  # Beginner, Intermediate, Advanced
    expected_features = Column(JSON, nullable=True)
    technology_stack = Column(JSON, nullable=True)
    learning_outcomes = Column(JSON, nullable=True)
    resume_value = Column(Text, nullable=True)
    suggested_extensions = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    profile = relationship("CandidateProfile", back_populates="project_recommendations")
