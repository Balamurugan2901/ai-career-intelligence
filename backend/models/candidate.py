import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from backend.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    raw_text = Column(Text, nullable=False)
    file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="resumes")
    profile = relationship("CandidateProfile", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="resume", cascade="all, delete-orphan")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    professional_summary = Column(Text, nullable=True)
    years_of_experience = Column(Float, default=0.0)
    
    # Store complete structured output JSON safely
    profile_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    resume = relationship("Resume", back_populates="profile")
    candidate_skills = relationship("CandidateSkill", back_populates="profile", cascade="all, delete-orphan")
    career_paths = relationship("CareerPath", back_populates="profile", cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="profile", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="profile", cascade="all, delete-orphan")
    project_recommendations = relationship("ProjectRecommendation", back_populates="profile", cascade="all, delete-orphan")
    interview_questions = relationship("InterviewQuestion", back_populates="profile", cascade="all, delete-orphan")
