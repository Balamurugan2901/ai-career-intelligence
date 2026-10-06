import pytest
from unittest.mock import patch
from sqlalchemy.orm import Session

from backend.models.database import Base, engine, SessionLocal
from backend.models.candidate import CandidateProfile, Resume
from backend.models.interview import AnalysisRun

from backend.orchestration.pipeline import CareerAnalysisPipeline, pipeline_orchestrator
from backend.orchestration.cache import pipeline_cache
from backend.schemas.analysis import FullAnalysisSummaryResponse


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create test candidate resume & profile
    resume = Resume(
        filename="test_pipeline_resume.pdf",
        file_type="pdf",
        raw_text="Experienced Senior Software Engineer proficient in Python, FastAPI, Docker, and PostgreSQL.",
    )

    db.add(resume)
    db.commit()

    profile = CandidateProfile(
        resume_id=resume.id,
        name="Pipeline Candidate",
        professional_summary="Senior Engineer specializing in Python, FastAPI, and AI applications.",
        years_of_experience=5.0,
        profile_json={
            "name": "Pipeline Candidate",
            "professional_summary": "Senior Engineer specializing in Python, FastAPI, and AI applications.",
            "years_of_experience": 5.0,
            "skills": {
                "programming_languages": ["Python", "SQL"],
                "frameworks": ["FastAPI"],
                "cloud_tools": ["Docker", "Git"],
                "databases": ["PostgreSQL"],
            },
        },
    )
    db.add(profile)
    db.commit()

    yield db, profile.id

    db.close()


def test_full_pipeline_execution_and_evidence(setup_db):
    """Test full pipeline execution, stage logging, and evidence aggregation."""
    db, candidate_id = setup_db
    pipeline_cache.clear()

    res: FullAnalysisSummaryResponse = CareerAnalysisPipeline.execute(
        db=db,
        candidate_id=candidate_id,
        target_role="GenAI Engineer",
    )

    assert res.candidate_id == candidate_id
    assert res.target_role == "GenAI Engineer"
    assert res.cached is False
    assert isinstance(res.evidence_sources, list)
    assert len(res.evidence_sources) > 0

    # Verify AnalysisRun record in DB
    run_rec = db.query(AnalysisRun).filter(AnalysisRun.id == res.analysis_id).first()
    assert run_rec is not None
    assert run_rec.status == "COMPLETED"
    assert len(run_rec.agents_completed) == 7


def test_pipeline_cache_hit_behavior(setup_db):
    """Test second execution with identical inputs returns instantly from cache."""
    db, candidate_id = setup_db

    # First run to populate cache
    res1 = CareerAnalysisPipeline.execute(db=db, candidate_id=candidate_id, target_role="GenAI Engineer")

    # Second run should HIT cache
    res2 = CareerAnalysisPipeline.execute(db=db, candidate_id=candidate_id, target_role="GenAI Engineer")

    assert res2.cached is True
    assert res2.candidate_id == candidate_id
    assert res2.target_role == "GenAI Engineer"
    assert len(res2.evidence_sources) == len(res1.evidence_sources)


def test_pipeline_cache_invalidation_on_target_role_change(setup_db):
    """Test changing target role invalidates cache and triggers new execution."""
    db, candidate_id = setup_db

    res1 = CareerAnalysisPipeline.execute(db=db, candidate_id=candidate_id, target_role="GenAI Engineer")

    # Change target role to Backend Developer
    res2 = CareerAnalysisPipeline.execute(db=db, candidate_id=candidate_id, target_role="Backend Developer")

    assert res2.target_role == "Backend Developer"
    assert res2.cached is False

