from backend.services.market.market_service import market_service
from backend.services.market.reference_provider import ReferenceMarketProvider


def test_reference_market_provider_load():
    """Verifies reference market provider loads curated dataset."""
    provider = ReferenceMarketProvider()
    data = provider.get_all_market_data()
    assert len(data) >= 10
    assert "GenAI Engineer" in data
    assert "AI Engineer" in data


def test_market_service_role_demand():
    """Verifies MarketService returns normalized role demand dictionary."""
    demand = market_service.get_role_demand("GenAI Engineer")
    assert demand["role_name"] == "GenAI Engineer"
    assert demand["demand_level"] in ["HIGH DEMAND", "MEDIUM DEMAND", "LOWER PRIORITY"]
    assert "Python" in demand["top_required_skills"]
    assert "data_source" in demand
    assert "Market insight based on configured reference data" in demand["data_source"]


def test_market_service_unknown_role_fallback():
    """Verifies fallback data returned for unregistered role title."""
    demand = market_service.get_role_demand("Quantum Computing Specialist")
    assert demand["role_name"] == "Quantum Computing Specialist"
    assert demand["demand_level"] == "MEDIUM DEMAND"
    assert "Market insight based on configured reference data" in demand["data_source"]
