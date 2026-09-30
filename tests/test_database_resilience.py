import io
import fitz
import pytest
from unittest.mock import patch

from backend.models.database import SessionLocal
from backend.orchestration.pipeline import CareerAnalysisPipeline
from backend.models.interview import AnalysisRun
from backend.repositories.candidate_repository import CandidateRepository
from backend.repositories.career_repository import CareerRepository


def create_test_pdf_file():
    """Generates an in-memory PDF tuple for FastAPI test upload."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Rivera\nEmail: alex.rivera.idempotency@example.com\nSenior Backend Engineer with 4 years Python and PostgreSQL experience."
    )
    pdf_bytes = doc.write()
    doc.close()
    return ("alex_rivera_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")


def test_pipeline_reanalysis_idempotency(client):
    """Verifies running pipeline analysis multiple times for the same candidate is fully idempotent."""
    # 1. Upload candidate resume
    file_tuple = create_test_pdf_file()
    res1 = client.post("/resume/upload", files={"file": file_tuple})
    assert res1.status_code == 201
    candidate_id = res1.json()["candidate_id"]

    db = SessionLocal()
    try:
        # 2. Run Pipeline Analysis Run #1
        run1 = CareerAnalysisPipeline.execute(db, candidate_id=candidate_id, target_role="AI Engineer")
        assert run1.analysis_id is not None

        # 3. Run Pipeline Analysis Run #2 for the exact same candidate
        run2 = CareerAnalysisPipeline.execute(db, candidate_id=candidate_id, target_role="GenAI Engineer")
        assert run2.analysis_id is not None
        assert run2.analysis_id != run1.analysis_id

        # 4. Verify database state
        runs = db.query(AnalysisRun).filter(AnalysisRun.id.in_([run1.analysis_id, run2.analysis_id])).all()
        assert len(runs) == 2
        career_paths = CareerRepository.get_career_paths_by_candidate_id(db, candidate_id)
        assert len(career_paths) > 0
    finally:
        db.close()




def test_pipeline_transaction_integrity_on_failure(client):
    """Verifies database records AnalysisRun as FAILED when an agent throws an exception mid-pipeline."""
    file_tuple = create_test_pdf_file()
    res = client.post("/resume/upload", files={"file": file_tuple})
    assert res.status_code == 201
    candidate_id = res.json()["candidate_id"]

    db = SessionLocal()
    try:
        with patch("backend.orchestration.pipeline.skill_gap_agent.analyze_candidate_gaps", side_effect=RuntimeError("Simulated Skill Gap Agent Crash")):
            with pytest.raises(RuntimeError) as exc_info:
                CareerAnalysisPipeline.execute(db, candidate_id=candidate_id, target_role="AI Engineer")
            assert "Simulated Skill Gap Agent Crash" in str(exc_info.value)

            # Check AnalysisRun status in DB
            failed_run = db.query(AnalysisRun).order_by(AnalysisRun.id.desc()).first()
            assert failed_run is not None
            assert failed_run.status == "FAILED"
            assert "Simulated Skill Gap Agent Crash" in failed_run.error_message
            assert len(failed_run.agents_completed) == 3  # Stages 1, 2, 3 completed before stage 4 failed
    finally:
        db.close()
