import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from backend.models.database import Base


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id"), nullable=False)
    category = Column(String(100), nullable=False)  # Resume, Project, Technical, Coding, AI/ML, GenAI, Behavioral, HR
    question = Column(Text, nullable=False)
    difficulty = Column(String(50), default="Medium")  # Easy, Medium, Hard
    expected_concepts = Column(JSON, nullable=True)
    evaluation_points = Column(JSON, nullable=True)
    model_answer_structure = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    profile = relationship("CandidateProfile", back_populates="interview_questions")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, RUNNING, COMPLETED, FAILED
    execution_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    agents_completed = Column(JSON, nullable=True)  # List of completed agent names
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    resume = relationship("Resume", back_populates="analysis_runs")
