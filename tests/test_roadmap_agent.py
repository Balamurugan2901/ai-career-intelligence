from backend.agents.roadmap_agent import roadmap_agent
from backend.schemas.candidate import CandidateProfileSchema, CategorizedSkills
from backend.schemas.roadmap import LearningRoadmapResponse, RoadmapPhaseSchema
from backend.schemas.skill_gap import SkillGapItem


def test_roadmap_agent_generate():
    """Verifies LearningRoadmapAgent creates structured 6-phase roadmap with progressive sequencing."""
    profile = CandidateProfileSchema(
        name="Alex Morgan",
        professional_summary="Backend Developer.",
        years_of_experience=2.0,
        skills=CategorizedSkills(programming_languages=["Python"], frameworks=["FastAPI"]),
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
            dependency_skills=["Python", "FastAPI"],
        ),
        SkillGapItem(
            skill="RAG (Retrieval-Augmented Generation)",
            current_level="None",
            target_level="Advanced",
            priority="HIGH",
            gap_type="missing",
            reason="Core GenAI requirement",
            estimated_learning_effort="3 weeks",
            dependency_skills=["Vector Databases"],
        ),
    ]

    res = roadmap_agent.generate_roadmap(profile, "GenAI Engineer", gaps, candidate_id=1)

    assert isinstance(res, LearningRoadmapResponse)
    assert res.target_role == "GenAI Engineer"
    assert res.total_phases == 6
    assert len(res.phases) == 6

    # Verify phase order
    phase_names = [p.phase_name for p in res.phases]
    assert "Foundations" in phase_names[0]
    assert "Core" in phase_names[1]
    assert "Advanced" in phase_names[2]
    assert "GenAI" in phase_names[3]
    assert "Projects" in phase_names[4]
    assert "Interview" in phase_names[5]

    for p in res.phases:
        assert isinstance(p, RoadmapPhaseSchema)
        assert len(p.items) > 0
        for item in p.items:
            assert len(item.skill) > 0
            assert len(item.practical_task) > 0
            assert len(item.validation_method) > 0
