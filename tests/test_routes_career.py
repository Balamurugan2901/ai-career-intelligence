import io
import fitz


def upload_sample_resume(client):
    """Helper to upload a sample resume and return candidate_id."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Morgan\nEmail: alex.morgan@example.com\nPython, FastAPI, React, SQL, Docker, RAG, LangChain, Machine Learning."
    )
    pdf_bytes = doc.write()
    doc.close()

    res = client.post(
        "/resume/upload",
        files={"file": ("alex_career.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    assert res.status_code == 201
    return res.json()["candidate_id"]


def test_career_matching_flow(client):
    """Verifies POST /career/match/{id} and GET /career/matches/{id} API endpoints."""
    candidate_id = upload_sample_resume(client)

    # 1. Trigger POST /career/match/{candidate_id}
    match_res = client.post(f"/career/match/{candidate_id}?top_n=4")
    assert match_res.status_code == 200
    data = match_res.json()

    assert data["candidate_id"] == candidate_id
    assert data["total_matches"] == 4
    assert len(data["career_paths"]) == 4

    top_role = data["career_paths"][0]
    assert "role_name" in top_role
    assert "fit_score" in top_role
    assert "reasoning" in top_role
    assert "recommended_next_step" in top_role

    # 2. Retrieve GET /career/matches/{candidate_id} from SQLite DB
    get_res = client.get(f"/career/matches/{candidate_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["candidate_id"] == candidate_id
    assert get_data["total_matches"] == 4
    assert get_data["career_paths"][0]["role_name"] == top_role["role_name"]


def test_career_match_not_found(client):
    """Verifies 404 returned for non-existent candidate_id."""
    res = client.post("/career/match/99999")
    assert res.status_code == 404
