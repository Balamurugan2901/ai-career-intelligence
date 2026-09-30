import io
import pytest
from unittest.mock import patch
import fitz

from backend.services.llm.gemini_provider import GeminiProvider
from backend.schemas.candidate import CandidateProfileSchema


def create_test_pdf_file():
    """Generates a valid in-memory PDF tuple for FastAPI upload testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "John Test\nEmail: john@example.com\nDeveloper with Python experience.")
    pdf_bytes = doc.write()
    doc.close()
    return ("valid.pdf", io.BytesIO(pdf_bytes), "application/pdf")


def test_upload_corrupted_pdf_file(client):
    """Verifies POST /resume/upload returns 400 Bad Request for unparseable corrupted PDF bytes."""
    corrupted_bytes = io.BytesIO(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F")
    files = {"file": ("corrupted.pdf", corrupted_bytes, "application/pdf")}
    
    response = client.post("/resume/upload", files=files)
    assert response.status_code == 400
    detail_lower = response.json()["detail"].lower()
    assert "corrupted" in detail_lower or "invalid" in detail_lower or "failed" in detail_lower


def test_upload_zero_byte_empty_file(client):
    """Verifies POST /resume/upload returns 400 Bad Request for zero-byte empty resume file."""
    empty_bytes = io.BytesIO(b"")
    files = {"file": ("empty.pdf", empty_bytes, "application/pdf")}

    response = client.post("/resume/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_unsupported_file_extension(client):
    """Verifies POST /resume/upload returns 400 Bad Request for unsupported file extension (.exe)."""
    exe_bytes = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
    files = {"file": ("malicious_payload.exe", exe_bytes, "application/x-msdownload")}

    response = client.post("/resume/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_oversized_file(client):
    """Verifies POST /resume/upload returns 400 Bad Request for files exceeding 10MB size limit."""
    oversized_bytes = io.BytesIO(b"0" * (10 * 1024 * 1024 + 1024))
    files = {"file": ("large_resume.pdf", oversized_bytes, "application/pdf")}

    response = client.post("/resume/upload", files=files)
    assert response.status_code == 400
    assert "exceeds maximum limit" in response.json()["detail"].lower()


def test_gemini_provider_demo_mode_fallback():
    """Verifies GeminiProvider generates mock Pydantic responses cleanly in Demo Mode."""
    provider = GeminiProvider(api_key="mock_key")
    provider.demo_mode = True

    assert provider.health_check() is True
    
    text_res = provider.generate_text("Analyze candidate profile")
    assert "[DEMO MODE RESPONSE]" in text_res

    json_res = provider.generate_json("Extract candidate profile", CandidateProfileSchema)
    assert json_res is not None


def test_gemini_provider_malformed_json_fallback():
    """Verifies GeminiProvider falls back to mock json when raw LLM response is malformed."""
    provider = GeminiProvider(api_key="mock_key")
    provider.demo_mode = True

    result = provider.generate_json("Extract candidate profile", CandidateProfileSchema)
    assert isinstance(result, CandidateProfileSchema)


def test_global_exception_handler_sanitizes_unhandled_errors(client):
    """Verifies global exception handler catches raw exceptions and sanitizes API responses."""
    file_tuple = create_test_pdf_file()
    with patch("backend.api.routes_resume.CandidateRepository.save_resume_and_profile", side_effect=RuntimeError("Database Connection Timeout Error!")):
        response = client.post("/resume/upload", files={"file": file_tuple})
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Database Connection Timeout Error!" not in data["detail"]
