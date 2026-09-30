import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.models.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    normalized_name = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(100), index=True, nullable=True)  # e.g., technical, framework, db, cloud, ai_ml

    candidate_skills = relationship("CandidateSkill", back_populates="skill")
    career_requirements = relationship("CareerRequirement", back_populates="skill")
    skill_gaps = relationship("SkillGap", back_populates="skill")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(String(50), default="Intermediate")  # Beginner, Intermediate, Advanced, Expert
    
    profile = relationship("CandidateProfile", back_populates="candidate_skills")
    skill = relationship("Skill", back_populates="candidate_skills")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    target_role = Column(String(255), nullable=True)
    current_level = Column(String(50), default="None")
    target_level = Column(String(50), default="Intermediate")
    priority = Column(String(20), default="MEDIUM")  # HIGH, MEDIUM, LOW
    reason = Column(Text, nullable=True)
    estimated_learning_effort = Column(String(100), nullable=True)
    dependency_skills = Column(JSON, nullable=True)  # List of skill names

    profile = relationship("CandidateProfile", back_populates="skill_gaps")
    skill = relationship("Skill", back_populates="skill_gaps")
