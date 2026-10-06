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
from backend.mcp.schemas import MCPToolResult


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


def test_career_agent_mcp_integration(mock_candidate_profile):
    """Test CareerMatchingAgent includes MCP source in output."""
    results = career_agent.match_career_paths(profile=mock_candidate_profile, top_n=2)
    assert len(results) > 0
    sources = results[0].sources
    mcp_sources = [s for s in sources if s.get("source") == "MCP Local Reference Provider"]
    assert len(mcp_sources) > 0
    assert mcp_sources[0]["tool"] == "get_role_requirements"


def test_market_agent_mcp_integration():
    """Test MarketIntelligenceAgent includes MCP source in output."""
    res = market_agent.analyze_single_role("GenAI Engineer")
    mcp_sources = [s for s in res.sources if s.get("source") == "MCP Local Reference Provider"]
    assert len(mcp_sources) > 0
    assert mcp_sources[0]["tool"] == "get_market_benchmark"


def test_skill_gap_agent_mcp_integration(mock_candidate_profile):
    """Test SkillGapAgent includes MCP source in output."""
    res = skill_gap_agent.analyze_candidate_gaps(profile=mock_candidate_profile, target_role="GenAI Engineer")
    mcp_sources = [s for s in res.sources if s.get("source") == "MCP Local Reference Provider"]
    assert len(mcp_sources) > 0
    assert mcp_sources[0]["tool"] == "search_skill_dependencies"


def test_roadmap_agent_mcp_integration(mock_candidate_profile, mock_skill_gaps):
    """Test LearningRoadmapAgent includes MCP source in output."""
    res = roadmap_agent.generate_roadmap(profile=mock_candidate_profile, target_role="GenAI Engineer", skill_gaps=mock_skill_gaps)
    mcp_sources = [s for s in res.sources if s.get("source") == "MCP Local Reference Provider"]
    assert len(mcp_sources) > 0
    assert mcp_sources[0]["tool"] == "search_learning_resources"


def test_project_agent_mcp_integration(mock_candidate_profile, mock_skill_gaps):
    """Test ProjectRecommendationAgent includes MCP source in output."""
    res = project_agent.recommend_projects(profile=mock_candidate_profile, target_role="GenAI Engineer", skill_gaps=mock_skill_gaps)
    mcp_sources = [s for s in res.sources if s.get("source") == "MCP Local Reference Provider"]
    assert len(mcp_sources) > 0
    assert mcp_sources[0]["tool"] == "search_jobs"


def test_interview_agent_mcp_integration(mock_candidate_profile, mock_skill_gaps):
    """Test InterviewPreparationAgent includes MCP source in output."""
    res = interview_agent.generate_interview_prep(profile=mock_candidate_profile, target_role="GenAI Engineer", skill_gaps=mock_skill_gaps)
    mcp_sources = [s for s in res.sources if s.get("source") == "MCP Local Reference Provider"]
    assert len(mcp_sources) > 0
    assert mcp_sources[0]["tool"] == "search_interview_bank"


def test_mcp_disabled_graceful_degradation_in_agents(mock_candidate_profile, mock_skill_gaps):
    """Test agents complete cleanly without MCP sources when MCP_ENABLED is False."""
    with patch.object(settings, "MCP_ENABLED", False):
        career_res = career_agent.match_career_paths(profile=mock_candidate_profile, top_n=2)
        assert len(career_res) > 0
        assert not any(s.get("source") == "MCP Local Reference Provider" for s in career_res[0].sources)

        market_res = market_agent.analyze_single_role("AI Engineer")
        assert not any(s.get("source") == "MCP Local Reference Provider" for s in market_res.sources)

        gap_res = skill_gap_agent.analyze_candidate_gaps(profile=mock_candidate_profile, target_role="AI Engineer")
        assert not any(s.get("source") == "MCP Local Reference Provider" for s in gap_res.sources)


def test_mcp_tool_failure_graceful_degradation(mock_candidate_profile):
    """Test agent resilience when MCP server returns an error tool result."""
    error_result = MCPToolResult(
        tool_name="get_market_benchmark",
        success=False,
        error="Simulated tool failure",
        source="MCP Local Reference Provider",
    )
    with patch("backend.mcp.server.mcp_server.call_tool", return_value=error_result):
        res = market_agent.analyze_single_role("Backend Developer")
        assert res.role_name == "Backend Developer"
        # Verify agent finishes without crashing
        assert res.demand_level is not None
