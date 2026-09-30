from backend.agents.skill_gap_agent import skill_gap_agent
from backend.schemas.candidate import CandidateProfileSchema, CategorizedSkills
from backend.schemas.skill_gap import SkillGapAnalysisResponse, SkillGapItem


def test_skill_gap_agent_analyze():
    """Verifies SkillGapAgent generates validated response with accurate summary metrics."""
    profile = CandidateProfileSchema(
        name="ML Developer",
        professional_summary="Machine Learning developer with Python and PyTorch.",
        years_of_experience=1.5,
        skills=CategorizedSkills(
            programming_languages=["Python"],
            frameworks=["PyTorch", "Scikit-Learn"],
            ai_ml_skills=["Machine Learning"],
        ),
    )

    response = skill_gap_agent.analyze_candidate_gaps(
        profile=profile,
        target_role="GenAI Engineer",
        candidate_id=1,
    )

    assert isinstance(response, SkillGapAnalysisResponse)
    assert response.target_role == "GenAI Engineer"
    assert response.total_gaps > 0
    assert response.matched_strengths_count > 0
    assert len(response.gaps) == response.total_gaps + response.matched_strengths_count

    for gap in response.gaps:
        assert isinstance(gap, SkillGapItem)
        assert len(gap.skill) > 0
        assert gap.priority in ["HIGH", "MEDIUM", "LOW"]
        assert len(gap.reason) > 0
