def test_root_endpoint(client):
    """Verifies API root endpoint returns 200 OK and expected structure."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "documentation" in data
    assert "health_check" in data


def test_health_endpoint(client):
    """Verifies /health endpoint returns 200 OK with database and LLM status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"] == "healthy"
    assert "llm_provider" in data
    assert "demo_mode" in data
    assert "model" in data
