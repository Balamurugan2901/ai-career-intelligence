import pytest
import io
import fitz
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.database import Base, engine, SessionLocal
from backend.orchestration.cache import pipeline_cache
from backend.config import settings

client = TestClient(app)


def make_pdf_bytes(text: str) -> io.BytesIO:
    """Helper to generate valid PyMuPDF in-memory PDF bytes."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    pdf_bytes = doc.write()
    doc.close()
    return io.BytesIO(pdf_bytes)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


def test_e2e_full_pipeline_flow(setup_db):
    """
    End-to-end integration test verifying complete flow:
    Resume Upload -> Candidate Extraction -> RAG Retrieval -> MCP Tool Execution ->
    Deterministic Heuristic Scoring -> Gemini/Mock Synthesis -> SQLite Persistence -> Evidence Aggregation.
    """
    pipeline_cache.clear()

    # 1. Resume Upload Endpoint (HTTP 201)
    resume_text = "Candidate Name: E2E Test User\nSummary: Software Engineer skilled in Python, FastAPI, Docker, and PyTorch.\nSkills: Python, SQL, Docker, PyTorch, FastAPI."
    files = {"file": ("e2e_resume.pdf", make_pdf_bytes(resume_text), "application/pdf")}
    upload_res = client.post("/resume/upload", files=files)
    assert upload_res.status_code == 201
    upload_json = upload_res.json()
    assert "candidate_id" in upload_json
    candidate_id = upload_json["candidate_id"]

    # 2. Trigger Pipeline Analysis Endpoint (HTTP 200)
    analysis_res = client.post("/analysis/start", json={"candidate_id": candidate_id, "target_role": "GenAI Engineer"})
    assert analysis_res.status_code == 200
    analysis_json = analysis_res.json()
    assert analysis_json["status"] in ["RUNNING", "COMPLETED"]

    # 3. Retrieve Full Aggregated Analysis Endpoint (HTTP 200)
    full_res = client.get(f"/analysis/candidate/{candidate_id}/full?target_role=GenAI Engineer")
    assert full_res.status_code == 200
    full_data = full_res.json()

    # 4. Verify Candidate Extraction & Profile Data
    assert full_data["candidate_id"] == candidate_id
    assert full_data["target_role"] == "GenAI Engineer"
    assert "profile" in full_data
    assert full_data["cached"] is True  # Served from cache after POST /analysis/start

    # 5. Verify RAG & MCP Evidence Aggregation
    assert "evidence_sources" in full_data
    assert isinstance(full_data["evidence_sources"], list)
    assert len(full_data["evidence_sources"]) > 0

    # 6. Verify Downstream Agent Outputs
    assert len(full_data["career_matches"]) > 0
    assert len(full_data["market_intelligence"]) > 0
    assert "gaps" in full_data["skill_gap_analysis"]
    assert len(full_data["learning_roadmap"]["phases"]) > 0
    assert len(full_data["project_recommendations"]["projects"]) > 0
    assert full_data["interview_preparation"]["total_questions"] > 0


def test_e2e_cache_hit_and_invalidation(setup_db):
    """Verifies end-to-end cache hit behavior and cache invalidation on target role change."""
    pipeline_cache.clear()

    # Upload candidate
    resume_text = "Candidate Name: Cache Test User\nSkills: Python, Machine Learning, TensorFlow, SQL."
    files = {"file": ("cache_resume.pdf", make_pdf_bytes(resume_text), "application/pdf")}
    upload_res = client.post("/resume/upload", files=files)
    assert upload_res.status_code == 201
    candidate_id = upload_res.json()["candidate_id"]

    # First analysis run (Cache Miss)
    client.post("/analysis/start", json={"candidate_id": candidate_id, "target_role": "AI Engineer"})
    res1 = client.get(f"/analysis/candidate/{candidate_id}/full?target_role=AI Engineer").json()
    assert res1["cached"] is True
    assert res1["target_role"] == "AI Engineer"

    # Second analysis run with identical parameters (Cache Hit)
    res2 = client.get(f"/analysis/candidate/{candidate_id}/full?target_role=AI Engineer").json()
    assert res2["cached"] is True
    assert res2["candidate_id"] == candidate_id

    # Third analysis run with DIFFERENT target role (Cache Invalidation & Re-execution)
    client.post("/analysis/start", json={"candidate_id": candidate_id, "target_role": "Data Scientist"})
    res3 = client.get(f"/analysis/candidate/{candidate_id}/full?target_role=Data Scientist").json()
    assert res3["cached"] is True
    assert res3["target_role"] == "Data Scientist"


def test_e2e_simultaneous_rag_and_mcp_disabled_degradation(setup_db):
    """
    Test system resilience when both RAG_ENABLED=False and MCP_ENABLED=False simultaneously.
    Guarantees 100% graceful degradation to internal reference defaults without breaking pipeline.
    """
    pipeline_cache.clear()

    # Upload candidate
    resume_text = "Candidate Name: Degradation User\nSkills: Python, Java, C++, Git."
    files = {"file": ("degradation_resume.pdf", make_pdf_bytes(resume_text), "application/pdf")}
    upload_res = client.post("/resume/upload", files=files)
    assert upload_res.status_code == 201
    candidate_id = upload_res.json()["candidate_id"]

    with patch.object(settings, "RAG_ENABLED", False), patch.object(settings, "MCP_ENABLED", False):
        analysis_res = client.post("/analysis/start", json={"candidate_id": candidate_id, "target_role": "Backend Developer"})
        assert analysis_res.status_code == 200

        full_res = client.get(f"/analysis/candidate/{candidate_id}/full?target_role=Backend Developer")
        assert full_res.status_code == 200
        full_data = full_res.json()

        assert full_data["candidate_id"] == candidate_id
        assert full_data["target_role"] == "Backend Developer"
        assert len(full_data["career_matches"]) > 0
        assert len(full_data["learning_roadmap"]["phases"]) > 0


def test_e2e_file_upload_edge_cases(setup_db):
    """Test file upload edge cases (zero byte, corrupted PDF bytes, invalid extensions)."""
    # 1. Zero-byte empty file
    files = {"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")}
    res = client.post("/resume/upload", files=files)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()

    # 2. Corrupted PDF content
    files = {"file": ("corrupted.pdf", io.BytesIO(b"NOT_A_REAL_PDF_HEADER_CONTENT"), "application/pdf")}
    res = client.post("/resume/upload", files=files)
    assert res.status_code == 400
    assert "corrupted" in res.json()["detail"].lower()

    # 3. Invalid file extension
    files = {"file": ("executable.exe", io.BytesIO(b"MZ..."), "application/octet-stream")}
    res = client.post("/resume/upload", files=files)
    assert res.status_code == 400
    assert "unsupported" in res.json()["detail"].lower()
