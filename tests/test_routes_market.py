import io
import fitz


def setup_candidate_and_matches(client):
    """Helper to upload resume and calculate career matches."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "Alex Morgan\nPython, FastAPI, LangChain, RAG, PyTorch, Docker, AWS."
    )
    pdf_bytes = doc.write()
    doc.close()

    upload_res = client.post(
        "/resume/upload",
        files={"file": ("alex_mkt.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
    )
    cand_id = upload_res.json()["candidate_id"]
    client.post(f"/career/match/{cand_id}?top_n=3")
    return cand_id


def test_get_market_role_demand_endpoint(client):
    """Verifies GET /market/role/{role_name} API endpoint."""
    res = client.get("/market/role/GenAI Engineer")
    assert res.status_code == 200
    data = res.json()
    assert data["role_name"] == "GenAI Engineer"
    assert data["demand_level"] in ["HIGH DEMAND", "MEDIUM DEMAND", "LOWER PRIORITY"]
    assert "data_source" in data


def test_analyze_market_for_candidate_endpoint(client):
    """Verifies POST /market/analyze/{candidate_id} API endpoint and DB requirement storage."""
    cand_id = setup_candidate_and_matches(client)

    res = client.post(f"/market/analyze/{cand_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["candidate_id"] == cand_id
    assert data["analyzed_roles_count"] > 0
    assert len(data["market_demands"]) > 0
    assert "demand_level" in data["market_demands"][0]


def test_market_analyze_not_found(client):
    """Verifies 404 for invalid candidate_id."""
    res = client.post("/market/analyze/99999")
    assert res.status_code == 404
