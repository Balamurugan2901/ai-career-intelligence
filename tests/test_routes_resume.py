import io
import fitz


def create_test_pdf_file():
    """Generates an in-memory PDF tuple for FastAPI TestClient file upload."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Morgan\nEmail: alex@example.com\nSoftware Engineer with 2 years Python and FastAPI experience."
    )
    pdf_bytes = doc.write()
    doc.close()
    return ("alex_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")


def test_upload_resume_endpoint_success(client):
    """Verifies POST /resume/upload succeeds and stores candidate profile."""
    file_tuple = create_test_pdf_file()

    response = client.post(
        "/resume/upload",
        files={"file": file_tuple},
    )

    assert response.status_code == 201
    data = response.json()
    assert "resume_id" in data
    assert "candidate_id" in data
    assert data["filename"] == "alex_resume.pdf"
    assert data["file_type"] == ".pdf"
    assert "profile" in data
    assert data["profile"]["name"] is not None

    # Test GET /resume/candidate/{candidate_id}
    candidate_id = data["candidate_id"]
    get_res = client.get(f"/resume/candidate/{candidate_id}")
    assert get_res.status_code == 200
    candidate_data = get_res.json()
    assert candidate_data["name"] == data["profile"]["name"]


def test_upload_resume_endpoint_invalid_extension(client):
    """Verifies POST /resume/upload returns 400 for unsupported format."""
    files = {"file": ("test.txt", io.BytesIO(b"Hello text file"), "text/plain")}
    response = client.post("/resume/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]
