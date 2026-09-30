from backend.agents.project_agent import project_agent
from backend.schemas.candidate import CandidateProfileSchema, CategorizedSkills
from backend.schemas.projects import ProjectRecommendationResponse, ProjectItemSchema
from backend.schemas.skill_gap import SkillGapItem


def test_project_agent_recommendations():
    """Verifies ProjectRecommendationAgent generates 3 tailored project items following difficulty ladder."""
    profile = CandidateProfileSchema(
        name="Alex Morgan",
        professional_summary="Junior Developer learning GenAI.",
        years_of_experience=1.0,
        skills=CategorizedSkills(programming_languages=["Python"]),
    )

    gaps = [
        SkillGapItem(
            skill="LangChain",
            current_level="None",
            target_level="Intermediate",
            priority="HIGH",
            gap_type="missing",
            reason="High demand",
            estimated_learning_effort="2 weeks",
        ),
        SkillGapItem(
            skill="RAG (Retrieval-Augmented Generation)",
            current_level="None",
            target_level="Advanced",
            priority="HIGH",
            gap_type="missing",
            reason="Core requirement",
            estimated_learning_effort="3 weeks",
        ),
    ]

    res = project_agent.recommend_projects(profile, "GenAI Engineer", gaps, candidate_id=1)

    assert isinstance(res, ProjectRecommendationResponse)
    assert res.target_role == "GenAI Engineer"
    assert res.total_projects == 3
    assert len(res.projects) == 3

    # Difficulty ladder check
    assert res.projects[0].difficulty == "Beginner"
    assert res.projects[1].difficulty == "Intermediate"
    assert res.projects[2].difficulty == "Advanced"

    for proj in res.projects:
        assert isinstance(proj, ProjectItemSchema)
        assert len(proj.project_title) > 0
        assert len(proj.why_this_project) > 0
        assert len(proj.technology_stack) > 0
        assert len(proj.resume_value) > 0
