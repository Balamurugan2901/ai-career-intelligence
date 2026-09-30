from backend.schemas.candidate import CandidateProfileSchema, CategorizedSkills
from backend.services.gap_analyzer import gap_analyzer


def test_gap_analyzer_categorization():
    """Verifies candidate with partial skills gets strength for matched skills and missing/high priority for required gaps."""
    profile = CandidateProfileSchema(
        name="Alex Morgan",
        professional_summary="Backend Developer with Python and FastAPI experience.",
        years_of_experience=2.0,
        skills=CategorizedSkills(
            programming_languages=["Python"],
            frameworks=["FastAPI"],
            cloud_tools=["Git"],
        ),
    )

    gaps = gap_analyzer.analyze_gaps(profile, target_role_name="GenAI Engineer")
    gap_skills = {g["skill"].lower(): g for g in gaps}

    # Python & FastAPI should be strength
    assert gap_skills["python"]["gap_type"] == "strength"
    assert gap_skills["fastapi"]["gap_type"] == "strength"

    # LangChain & RAG should be missing with HIGH priority
    assert gap_skills["langchain"]["gap_type"] == "missing"
    assert gap_skills["langchain"]["priority"] == "HIGH"
    assert "Python" in gap_skills["langchain"]["dependency_skills"]
