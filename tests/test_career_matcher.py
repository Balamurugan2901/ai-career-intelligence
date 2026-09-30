from backend.schemas.candidate import (
    CandidateProfileSchema,
    CategorizedSkills,
    EducationItem,
    ProjectItem,
)
from backend.services.career_matcher import career_matcher, TARGET_ROLES


def test_career_matcher_full_match():
    """Verifies candidate with GenAI stack gets high fit score for GenAI Engineer."""
    profile = CandidateProfileSchema(
        name="GenAI Expert",
        professional_summary="Senior Engineer specializing in RAG and LLM applications.",
        years_of_experience=3.0,
        skills=CategorizedSkills(
            programming_languages=["Python"],
            frameworks=["FastAPI", "LangChain"],
            databases=["Vector Databases", "ChromaDB"],
            cloud_tools=["Docker", "AWS"],
            ai_ml_skills=["Machine Learning", "Deep Learning", "PyTorch"],
            genai_skills=["RAG (Retrieval-Augmented Generation)", "Large Language Models", "Prompt Engineering"],
        ),
        education=[EducationItem(degree="B.S. in Computer Science", institution="State Univ")],
        projects=[ProjectItem(title="RAG App", description="Built RAG with LangChain", technologies_used=["Python", "LangChain", "ChromaDB"])],
    )

    matches = career_matcher.evaluate_all_matches(profile, top_n=5)
    assert len(matches) == 5
    top_match = matches[0]
    assert top_match["role_name"] == "GenAI Engineer"
    assert top_match["fit_score"] >= 80.0
    assert "Python" in top_match["matching_skills"]


def test_career_matcher_zero_skills():
    """Verifies candidate with minimal skills gets low score without errors."""
    profile = CandidateProfileSchema(
        name="Novice",
        professional_summary="Beginner interested in tech.",
        years_of_experience=0.0,
        skills=CategorizedSkills(),
    )

    matches = career_matcher.evaluate_all_matches(profile, top_n=5)
    assert len(matches) == 5
    for m in matches:
        assert m["fit_score"] < 50.0
        assert len(m["missing_skills"]) > 0


def test_career_matcher_ranking_order():
    """Verifies results are sorted by fit_score descending."""
    profile = CandidateProfileSchema(
        name="Data Analyst",
        professional_summary="Data Analyst skilled in SQL and Pandas.",
        years_of_experience=2.0,
        skills=CategorizedSkills(
            programming_languages=["Python", "SQL"],
            frameworks=["Pandas"],
            other_skills=["Excel", "Data Visualization"],
        ),
    )

    matches = career_matcher.evaluate_all_matches(profile, top_n=10)
    for i in range(len(matches) - 1):
        assert matches[i]["fit_score"] >= matches[i + 1]["fit_score"]
