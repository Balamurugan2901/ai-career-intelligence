from backend.agents.career_agent import career_agent
from backend.schemas.candidate import CandidateProfileSchema, CategorizedSkills
from backend.schemas.career import CareerPathBase


def test_career_agent_match():
    """Verifies CareerMatchingAgent outputs structured CareerPathBase items with fit scores and reasoning."""
    profile = CandidateProfileSchema(
        name="Backend Dev",
        professional_summary="Backend Developer focused on Python FastAPI and PostgreSQL.",
        years_of_experience=2.0,
        skills=CategorizedSkills(
            programming_languages=["Python", "SQL"],
            frameworks=["FastAPI"],
            databases=["PostgreSQL"],
            cloud_tools=["Git", "Docker"],
        ),
    )

    results = career_agent.match_career_paths(profile, candidate_id=1, top_n=3)
    assert len(results) == 3
    for path in results:
        assert isinstance(path, CareerPathBase)
        assert len(path.role_name) > 0
        assert 0.0 <= path.fit_score <= 100.0
        assert len(path.reasoning) > 0
        assert len(path.recommended_next_step) > 0
