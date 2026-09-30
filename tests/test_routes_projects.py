import io
import fitz


def setup_candidate_profile(client):
    """Helper to upload resume and return candidate_id."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Morgan\nEmail: alex.proj@example.com\nPython, FastAPI, SQL, Docker, Machine Learning."
    )
    pdf_bytes = doc.write()
    doc.close()

    res = client.post(
        "/resume/upload",
        files={"file": ("alex_proj.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert res.status_code == 201
    return res.json()["candidate_id"]


def test_project_recommendations_flow(client):
    """Verifies POST /projects/recommend and GET /projects/{candidate_id} API endpoints."""
    cand_id = setup_candidate_profile(client)

    # 1. Trigger POST /projects/recommend/{candidate_id}?role_name=GenAI Engineer
    res = client.post(f"/projects/recommend/{cand_id}?role_name=GenAI Engineer")
    assert res.status_code == 200
    data = res.json()

    assert data["candidate_id"] == cand_id
    assert data["target_role"] == "GenAI Engineer"
    assert data["total_projects"] == 3
    assert len(data["projects"]) == 3

    # 2. Retrieve GET /projects/{candidate_id} from DB
    get_res = client.get(f"/projects/{cand_id}?role_name=GenAI Engineer")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["candidate_id"] == cand_id
    assert get_data["total_projects"] == 3
    assert get_data["projects"][0]["project_title"] == data["projects"][0]["project_title"]


def test_project_recommend_not_found(client):
    """Verifies 404 for invalid candidate_id."""
    res = client.post("/projects/recommend/99999")
    assert res.status_code == 404
