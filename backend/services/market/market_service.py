from typing import Dict, Any, Optional
from backend.services.market.base import BaseMarketProvider
from backend.services.market.reference_provider import ReferenceMarketProvider
from backend.utils.logger import logger


class MarketService:
    """Provider-agnostic Market Intelligence service layer."""

    def __init__(self, provider: Optional[BaseMarketProvider] = None):
        self.provider = provider or ReferenceMarketProvider()
        logger.info(f"MarketService initialized with provider: {self.provider.__class__.__name__}")

    def get_role_demand(self, role_name: str) -> Dict[str, Any]:
        """Returns market demand analysis dict for target role."""
        data = self.provider.get_role_market_data(role_name)
        if not data:
            return {
                "role_name": role_name,
                "demand_level": "MEDIUM DEMAND",
                "top_required_skills": [],
                "emerging_skills": [],
                "tools_and_frameworks": [],
                "cloud_technologies": [],
                "key_responsibilities": [],
                "salary_trend_summary": "Data unavailable.",
                "data_source": "Market insight based on configured reference data",
            }
        return data

    def get_all_roles_demand(self) -> Dict[str, Dict[str, Any]]:
        """Returns all reference market roles."""
        return self.provider.get_all_market_data()


# Singleton instance
market_service = MarketService()
