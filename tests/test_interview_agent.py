from backend.agents.interview_agent import interview_agent
from backend.schemas.candidate import CandidateProfileSchema, CategorizedSkills, ProjectItem
from backend.schemas.interview import InterviewPreparationResponse, InterviewCategorySchema
from backend.schemas.skill_gap import SkillGapItem


def test_interview_agent_generation():
    """Verifies InterviewPreparationAgent generates questions covering all 8 categories."""
    profile = CandidateProfileSchema(
        name="Alex Morgan",
        professional_summary="Backend & GenAI developer.",
        years_of_experience=2.0,
        skills=CategorizedSkills(programming_languages=["Python"], frameworks=["FastAPI"]),
        projects=[ProjectItem(title="DocuBrain RAG System", description="PDF Q&A bot")],
    )

    gaps = [
        SkillGapItem(
            skill="LangChain",
            current_level="None",
            target_level="Intermediate",
            priority="HIGH",
            gap_type="missing",
            reason="Core gap",
            estimated_learning_effort="2 weeks",
        )
    ]

    res = interview_agent.generate_interview_prep(profile, "GenAI Engineer", gaps, candidate_id=1)

    assert isinstance(res, InterviewPreparationResponse)
    assert res.target_role == "GenAI Engineer"
    assert res.total_questions >= 8
    assert len(res.categories) == 8

    cat_names = [c.category_name for c in res.categories]
    expected_categories = [
        "Resume Questions",
        "Project Questions",
        "Technical Questions",
        "Coding Questions",
        "AI/ML Questions",
        "GenAI Questions",
        "Behavioral Questions",
        "HR Questions",
    ]

    for expected in expected_categories:
        assert expected in cat_names

    for cat in res.categories:
        assert isinstance(cat, InterviewCategorySchema)
        assert len(cat.questions) > 0
        for q in cat.questions:
            assert len(q.question) > 0
            assert len(q.model_answer_structure) > 0
