import pytest
from backend.models.database import SessionLocal
from backend.orchestration.pipeline import CareerAnalysisPipeline
from backend.models.interview import AnalysisRun
import io
import fitz


def create_test_pdf_tuple():
    """Generates an in-memory PDF tuple for FastAPI file upload testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Jane Doe\nEmail: jane.pipeline@example.com\nSenior AI Engineer with 4 years Python, PyTorch, and LLM experience."
    )
    pdf_bytes = doc.write()
    doc.close()
    return ("jane_pipeline_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")


def test_career_analysis_pipeline_full_execution(client):
    """Verifies end-to-end multi-agent pipeline sequential execution and database state tracking."""
    # 1. Prepare Candidate via upload endpoint
    file_tuple = create_test_pdf_tuple()
    upload_res = client.post("/resume/upload", files={"file": file_tuple})
    assert upload_res.status_code == 201
    candidate_id = upload_res.json()["candidate_id"]

    db = SessionLocal()
    try:
        # 2. Execute pipeline sequentially
        result = CareerAnalysisPipeline.execute(db, candidate_id=candidate_id, target_role="AI Engineer")

        # 3. Assert full analysis summary response structure
        assert result.candidate_id == candidate_id
        assert result.target_role == "AI Engineer"
        assert result.execution_time_seconds >= 0.0
        assert result.profile is not None
        assert len(result.career_matches) > 0
        assert len(result.market_intelligence) > 0
        assert result.skill_gap_analysis is not None
        assert result.learning_roadmap is not None
        assert len(result.project_recommendations.projects) > 0
        assert len(result.interview_preparation.categories) > 0

        # 4. Verify SQLite analysis_runs database state
        run_rec = db.query(AnalysisRun).filter(AnalysisRun.id == result.analysis_id).first()
        assert run_rec is not None
        assert run_rec.status == "COMPLETED"
        assert len(run_rec.agents_completed) == 7
        assert run_rec.agents_completed[0] == "Resume Intelligence Agent"
        assert run_rec.agents_completed[-1] == "Interview Preparation Agent"
        assert run_rec.completed_at is not None
    finally:
        db.close()


def test_career_analysis_pipeline_invalid_candidate(client):
    """Verifies pipeline error handling for non-existent candidate profile."""
    db = SessionLocal()
    try:
        with pytest.raises(ValueError) as exc_info:
            CareerAnalysisPipeline.execute(db, candidate_id=999999)
        assert "Candidate profile #999999 not found" in str(exc_info.value)
    finally:
        db.close()
