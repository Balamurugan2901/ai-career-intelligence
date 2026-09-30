import io
import fitz


def setup_candidate_profile(client):
    """Helper to upload resume and return candidate_id."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Morgan\nEmail: alex.rdm@example.com\nPython, FastAPI, SQL, Docker, Machine Learning."
    )
    pdf_bytes = doc.write()
    doc.close()

    res = client.post(
        "/resume/upload",
        files={"file": ("alex_rdm.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert res.status_code == 201
    return res.json()["candidate_id"]


def test_roadmap_generation_flow(client):
    """Verifies POST /roadmap/generate and GET /roadmap/{candidate_id} API endpoints."""
    cand_id = setup_candidate_profile(client)

    # 1. Trigger POST /roadmap/generate/{candidate_id}?role_name=GenAI Engineer
    res = client.post(f"/roadmap/generate/{cand_id}?role_name=GenAI Engineer")
    assert res.status_code == 200
    data = res.json()

    assert data["candidate_id"] == cand_id
    assert data["target_role"] == "GenAI Engineer"
    assert data["total_phases"] == 6
    assert len(data["phases"]) == 6

    # 2. Retrieve GET /roadmap/{candidate_id}?role_name=GenAI Engineer from DB
    get_res = client.get(f"/roadmap/{cand_id}?role_name=GenAI Engineer")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["candidate_id"] == cand_id
    assert get_data["target_role"] == "GenAI Engineer"
    assert get_data["total_phases"] == 6


def test_roadmap_not_found_handling(client):
    """Verifies 404 for invalid candidate_id."""
    res = client.post("/roadmap/generate/99999")
    assert res.status_code == 404
