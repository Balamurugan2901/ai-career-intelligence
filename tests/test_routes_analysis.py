import io
import fitz


def create_test_pdf_file():
    """Generates an in-memory PDF tuple for FastAPI TestClient file upload."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Bob Taylor\nEmail: bob.analysis@example.com\nData Scientist with 3 years Python, ML, and SQL experience."
    )
    pdf_bytes = doc.write()
    doc.close()
    return ("bob_resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")


def test_start_analysis_endpoint_success(client):
    """Verifies POST /analysis/start triggers the 7-agent orchestration pipeline successfully."""
    # 1. Upload resume
    file_tuple = create_test_pdf_file()
    upload_res = client.post("/resume/upload", files={"file": file_tuple})
    assert upload_res.status_code == 201
    candidate_id = upload_res.json()["candidate_id"]

    # 2. Trigger pipeline analysis
    payload = {
        "candidate_id": candidate_id,
        "target_role": "AI Engineer"
    }
    response = client.post("/analysis/start", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "analysis_id" in data
    assert data["candidate_id"] == candidate_id
    assert data["status"] == "COMPLETED"
    assert len(data["agents_completed"]) == 7
    assert data["execution_time_seconds"] >= 0.0

    # 3. Test GET /analysis/{analysis_id}
    analysis_id = data["analysis_id"]
    status_res = client.get(f"/analysis/{analysis_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["analysis_id"] == analysis_id
    assert status_data["status"] == "COMPLETED"
    assert len(status_data["agents_completed"]) == 7

    # 4. Test GET /analysis/candidate/{candidate_id}/full
    full_res = client.get(f"/analysis/candidate/{candidate_id}/full")
    assert full_res.status_code == 200
    full_data = full_res.json()
    assert full_data["candidate_id"] == candidate_id
    assert full_data["target_role"] == "AI Engineer"
    assert full_data["profile"]["name"] is not None
    assert len(full_data["career_matches"]) > 0
    assert len(full_data["market_intelligence"]) > 0
    assert "gaps" in full_data["skill_gap_analysis"]
    assert "phases" in full_data["learning_roadmap"]
    assert len(full_data["project_recommendations"]["projects"]) > 0
    assert len(full_data["interview_preparation"]["categories"]) > 0


def test_start_analysis_endpoint_not_found(client):
    """Verifies POST /analysis/start returns 404 for missing candidate_id."""
    payload = {"candidate_id": 999999, "target_role": "AI Engineer"}
    response = client.post("/analysis/start", json=payload)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_analysis_status_not_found(client):
    """Verifies GET /analysis/{analysis_id} returns 404 for missing analysis_id."""
    response = client.get("/analysis/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
