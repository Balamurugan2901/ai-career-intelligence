import io
import fitz


def setup_candidate_profile(client):
    """Helper to upload resume and return candidate_id."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Morgan\nEmail: alex.int@example.com\nPython, FastAPI, SQL, Docker, Machine Learning."
    )
    pdf_bytes = doc.write()
    doc.close()

    res = client.post(
        "/resume/upload",
        files={"file": ("alex_int.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert res.status_code == 201
    return res.json()["candidate_id"]


def test_interview_prep_flow(client):
    """Verifies POST /interview/generate and GET /interview/{candidate_id} API endpoints."""
    cand_id = setup_candidate_profile(client)

    # 1. Trigger POST /interview/generate/{candidate_id}?role_name=GenAI Engineer
    res = client.post(f"/interview/generate/{cand_id}?role_name=GenAI Engineer")
    assert res.status_code == 200
    data = res.json()

    assert data["candidate_id"] == cand_id
    assert data["target_role"] == "GenAI Engineer"
    assert data["total_questions"] >= 8
    assert len(data["categories"]) == 8

    # 2. Retrieve GET /interview/{candidate_id} from DB
    get_res = client.get(f"/interview/{cand_id}?role_name=GenAI Engineer")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["candidate_id"] == cand_id
    assert get_data["total_questions"] == data["total_questions"]
    assert len(get_data["categories"]) == 8


def test_interview_prep_not_found(client):
    """Verifies 404 for invalid candidate_id."""
    res = client.post("/interview/generate/99999")
    assert res.status_code == 404
