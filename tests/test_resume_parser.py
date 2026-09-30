import pytest
import fitz  # PyMuPDF
from backend.services.resume.parser import ResumeParser, ResumeParserError


def create_sample_pdf_bytes(text_content: str = "Alex Morgan Resume - Software Engineer with Python skills.") -> bytes:
    """Helper to generate an in-memory PDF byte stream for testing."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text_content)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes


def test_resume_parser_valid_pdf():
    """Verifies text extraction from valid PDF bytes."""
    pdf_bytes = create_sample_pdf_bytes("John Doe - Senior AI Engineer with Python and PyTorch experience.")
    extracted_text, ext = ResumeParser.parse_bytes("resume.pdf", pdf_bytes)
    assert ext == ".pdf"
    assert "John Doe" in extracted_text
    assert "Python" in extracted_text


def test_resume_parser_invalid_extension():
    """Verifies error raised on unsupported file extension."""
    with pytest.raises(ResumeParserError, match="Unsupported file format"):
        ResumeParser.parse_bytes("resume.txt", b"Dummy text content")


def test_resume_parser_empty_file():
    """Verifies error raised on empty content."""
    with pytest.raises(ResumeParserError, match="empty"):
        ResumeParser.parse_bytes("resume.pdf", b"")


def test_resume_parser_corrupted_file():
    """Verifies error raised on corrupted content."""
    with pytest.raises(ResumeParserError):
        ResumeParser.parse_bytes("corrupted.pdf", b"not a real pdf content header")
