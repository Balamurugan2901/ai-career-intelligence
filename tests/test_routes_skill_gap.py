import io
import fitz


def setup_candidate(client):
    """Helper to upload sample resume and return candidate_id."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Morgan\nEmail: alex.gap@example.com\nPython, FastAPI, SQL, Docker, Machine Learning."
    )
    pdf_bytes = doc.write()
    doc.close()

    res = client.post(
        "/resume/upload",
        files={"file": ("alex_gap.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert res.status_code == 201
    return res.json()["candidate_id"]


def test_skill_gap_analysis_flow(client):
    """Verifies POST /skill-gap/analyze and GET /skill-gap/{candidate_id} endpoints."""
    cand_id = setup_candidate(client)

    # 1. Trigger POST /skill-gap/analyze/{candidate_id}?role_name=GenAI Engineer
    res = client.post(f"/skill-gap/analyze/{cand_id}?role_name=GenAI Engineer")
    assert res.status_code == 200
    data = res.json()

    assert data["candidate_id"] == cand_id
    assert data["target_role"] == "GenAI Engineer"
    assert data["total_gaps"] > 0
    assert "high_priority_count" in data
    assert len(data["gaps"]) > 0

    # 2. Retrieve GET /skill-gap/{candidate_id}?role_name=GenAI Engineer from DB
    get_res = client.get(f"/skill-gap/{cand_id}?role_name=GenAI Engineer")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["candidate_id"] == cand_id
    assert get_data["target_role"] == "GenAI Engineer"
    assert get_data["total_gaps"] == data["total_gaps"]


def test_skill_gap_not_found(client):
    """Verifies 404 for invalid candidate_id."""
    res = client.post("/skill-gap/analyze/99999")
    assert res.status_code == 404
