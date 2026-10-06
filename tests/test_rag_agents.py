import pytest
from unittest.mock import patch

from backend.config import settings
from backend.agents.career_agent import career_agent
from backend.agents.market_agent import market_agent
from backend.agents.skill_gap_agent import skill_gap_agent
from backend.agents.roadmap_agent import roadmap_agent
from backend.agents.project_agent import project_agent
from backend.agents.interview_agent import interview_agent

from backend.schemas.candidate import CandidateProfileSchema, CategorizedSkills, WorkExperienceItem, ProjectItem
from backend.schemas.skill_gap import SkillGapItem


@pytest.fixture
def mock_candidate_profile():
    return CandidateProfileSchema(
        name="Test Candidate",
        email="test@example.com",
        phone="+1234567890",
        professional_summary="Senior Software Engineer specializing in Python, FastAPI, and AI applications.",
        years_of_experience=4.5,
        education=[],
        work_experience=[
            WorkExperienceItem(
                job_title="Software Developer",
                company="TechCorp",
                duration="2021 - Present",
                responsibilities=["Built REST APIs using Python and FastAPI.", "Managed PostgreSQL databases."],
            )
        ],
        skills=CategorizedSkills(
            programming_languages=["Python", "SQL"],
            frameworks=["FastAPI", "Flask"],
            cloud_tools=["Git", "Docker"],
            databases=["PostgreSQL"],
        ),
        projects=[
            ProjectItem(
                title="AI Career Search Platform",
                description="Built a career guidance tool using FastAPI and Python.",
                technologies_used=["Python", "FastAPI"],
            )
        ],
    )



@pytest.fixture
def mock_skill_gaps():
    return [
        SkillGapItem(
            skill="RAG (Retrieval-Augmented Generation)",
            current_level="None",
            target_level="Advanced",
            priority="HIGH",
            gap_type="missing_critical",
            reason="Vital for modern GenAI roles.",
            estimated_learning_effort="2-3 weeks",
            dependency_skills=["Python", "Vector Databases"],
        ),
        SkillGapItem(
            skill="Docker",
            current_level="Intermediate",
            target_level="Advanced",
            priority="MEDIUM",
            gap_type="depth_gap",
            reason="Important for production deployment.",
            estimated_learning_effort="1-2 weeks",
            dependency_skills=[],
        ),
    ]


def test_career_agent_rag_integration(mock_candidate_profile):
    """Test CareerMatchingAgent attaches RAG sources metadata."""
    results = career_agent.match_career_paths(profile=mock_candidate_profile, top_n=3)
    assert len(results) > 0
    assert isinstance(results[0].sources, list)


def test_market_agent_rag_integration():
    """Test MarketIntelligenceAgent attaches RAG sources metadata."""
    result = market_agent.analyze_single_role("GenAI Engineer")
    assert result.role_name == "GenAI Engineer"
    assert isinstance(result.sources, list)


def test_skill_gap_agent_rag_integration(mock_candidate_profile):
    """Test SkillGapAgent attaches RAG sources metadata."""
    result = skill_gap_agent.analyze_candidate_gaps(profile=mock_candidate_profile, target_role="GenAI Engineer")
    assert result.target_role == "GenAI Engineer"
    assert isinstance(result.sources, list)


def test_roadmap_agent_rag_integration(mock_candidate_profile, mock_skill_gaps):
    """Test LearningRoadmapAgent attaches RAG sources metadata."""
    result = roadmap_agent.generate_roadmap(
        profile=mock_candidate_profile,
        target_role="GenAI Engineer",
        skill_gaps=mock_skill_gaps,
    )
    assert result.target_role == "GenAI Engineer"
    assert len(result.phases) == 6
    assert isinstance(result.sources, list)


def test_project_agent_rag_integration(mock_candidate_profile, mock_skill_gaps):
    """Test ProjectRecommendationAgent attaches RAG sources metadata."""
    result = project_agent.recommend_projects(
        profile=mock_candidate_profile,
        target_role="GenAI Engineer",
        skill_gaps=mock_skill_gaps,
    )
    assert result.target_role == "GenAI Engineer"
    assert len(result.projects) == 3
    assert isinstance(result.sources, list)


def test_interview_agent_rag_integration(mock_candidate_profile, mock_skill_gaps):
    """Test InterviewPreparationAgent attaches RAG sources metadata."""
    result = interview_agent.generate_interview_prep(
        profile=mock_candidate_profile,
        target_role="GenAI Engineer",
        skill_gaps=mock_skill_gaps,
    )
    assert result.target_role == "GenAI Engineer"
    assert len(result.categories) == 8
    assert isinstance(result.sources, list)


def test_rag_disabled_graceful_degradation(mock_candidate_profile, mock_skill_gaps):
    """Test agents degrade gracefully when RAG_ENABLED and MCP_ENABLED are False."""
    with patch.object(settings, "RAG_ENABLED", False), patch.object(settings, "MCP_ENABLED", False):
        career_res = career_agent.match_career_paths(profile=mock_candidate_profile, top_n=2)
        assert len(career_res) > 0
        assert career_res[0].sources == []

        market_res = market_agent.analyze_single_role("Backend Developer")
        assert market_res.sources == []

        gap_res = skill_gap_agent.analyze_candidate_gaps(profile=mock_candidate_profile, target_role="Backend Developer")
        assert gap_res.sources == []

