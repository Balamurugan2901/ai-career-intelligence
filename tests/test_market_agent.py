from backend.agents.market_agent import market_agent
from backend.schemas.market import MarketRoleDemand


def test_market_agent_single_role():
    """Verifies MarketIntelligenceAgent processes single role."""
    demand = market_agent.analyze_single_role("AI Engineer")
    assert isinstance(demand, MarketRoleDemand)
    assert demand.role_name == "AI Engineer"
    assert demand.demand_level in ["HIGH DEMAND", "MEDIUM DEMAND", "LOWER PRIORITY"]
    assert len(demand.top_required_skills) > 0


def test_market_agent_multiple_roles():
    """Verifies MarketIntelligenceAgent processes batch list of roles."""
    roles = ["GenAI Engineer", "ML Engineer", "Backend Developer"]
    results = market_agent.analyze_market_for_roles(roles)
    assert len(results) == 3
    for res in results:
        assert isinstance(res, MarketRoleDemand)
        assert res.role_name in roles
