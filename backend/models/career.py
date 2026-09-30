import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from backend.models.database import Base


class CareerPath(Base):
    __tablename__ = "career_paths"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    role_name = Column(String(255), nullable=False)
    fit_score = Column(Float, nullable=False)  # 0.0 to 100.0 heuristic fit score
    reasoning = Column(Text, nullable=True)
    matching_skills = Column(JSON, nullable=True)  # List of matching skill names
    missing_skills = Column(JSON, nullable=True)   # List of missing skill names
    recommended_next_step = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    profile = relationship("CandidateProfile", back_populates="career_paths")
    requirements = relationship("CareerRequirement", back_populates="career_path", cascade="all, delete-orphan")


class CareerRequirement(Base):
    __tablename__ = "career_requirements"

    id = Column(Integer, primary_key=True, index=True)
    career_path_id = Column(Integer, ForeignKey("career_paths.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    demand_level = Column(String(50), default="HIGH DEMAND")  # HIGH DEMAND, MEDIUM DEMAND, LOWER PRIORITY
    importance = Column(String(50), default="Required")        # Required, Preferred

    career_path = relationship("CareerPath", back_populates="requirements")
    skill = relationship("Skill", back_populates="career_requirements")
