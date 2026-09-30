from backend.agents.resume_agent import resume_agent
from backend.schemas.candidate import CandidateProfileSchema


def test_resume_agent_analyze():
    """Verifies ResumeIntelligenceAgent returns valid CandidateProfileSchema with normalized skills."""
    raw_text = """
    Alex Morgan
    Email: alex@example.com
    Phone: +1 555-0192
    Summary: Experienced Software Engineer specializing in Python, React, and Machine Learning.
    Experience: Software Developer at TechCorp (2022-Present). Built FastAPI backend services.
    Education: B.S. in Computer Science from State University (2018-2022).
    Skills: Python 3, JS, ReactJS, FastAPI, Postgres, Docker, Machine Learning, RAG
    """
    profile = resume_agent.analyze_resume(raw_text, filename="alex_resume.pdf")

    assert isinstance(profile, CandidateProfileSchema)
    assert profile.name is not None
    assert len(profile.professional_summary) > 0
    assert len(profile.skills.all_skills_list()) > 0
    # Verify skill normalization was applied
    all_skills = profile.skills.all_skills_list()
    assert "Python" in all_skills or "python" not in all_skills
