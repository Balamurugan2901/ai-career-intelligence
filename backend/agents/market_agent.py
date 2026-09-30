from typing import List, Optional

from backend.config import settings
from backend.prompts.market.contextualize import (
    MARKET_CONTEXT_SYSTEM_INSTRUCTION,
    MARKET_CONTEXT_PROMPT_TEMPLATE,
)
from backend.schemas.market import MarketRoleDemand
from backend.services.llm.llm_service import LLMService, llm_service
from backend.services.market.market_service import MarketService, market_service
from backend.utils.logger import logger


class MarketIntelligenceAgent:
    """
    Agent 3: Market Intelligence Agent.
    Responsible for evaluating industry demand, skill requirements, emerging tech trends,
    and responsibilities for target career paths.
    """

    def __init__(
        self,
        llm_svc: Optional[LLMService] = None,
        mkt_svc: Optional[MarketService] = None,
    ):
        self.llm_service = llm_svc or llm_service
        self.market_service = mkt_svc or market_service

    def analyze_single_role(self, role_name: str) -> MarketRoleDemand:
        """Analyzes market demand data for a single target role."""
        raw_data = self.market_service.get_role_demand(role_name)

        if settings.is_demo_mode():
            return MarketRoleDemand.model_validate(raw_data)

        try:
            prompt = MARKET_CONTEXT_PROMPT_TEMPLATE.format(
                role_name=role_name,
                reference_data_json=raw_data,
            )
            return self.llm_service.generate_json(
                prompt=prompt,
                schema=MarketRoleDemand,
                system_instruction=MARKET_CONTEXT_SYSTEM_INSTRUCTION,
            )
        except Exception as e:
            logger.warning(f"MarketIntelligenceAgent API call failed for '{role_name}': {e}. Returning reference data.")
            return MarketRoleDemand.model_validate(raw_data)

    def analyze_market_for_roles(self, roles: List[str]) -> List[MarketRoleDemand]:
        """
        Analyzes market intelligence across a list of target role names.
        Returns list of validated MarketRoleDemand objects.
        """
        logger.info(f"MarketIntelligenceAgent analyzing market demand for {len(roles)} roles...")

        demands = []
        for role_name in roles:
            mkt_demand = self.analyze_single_role(role_name)
            demands.append(mkt_demand)

        logger.info(f"MarketIntelligenceAgent completed analysis for {len(demands)} market roles.")
        return demands


# Singleton agent instance
market_agent = MarketIntelligenceAgent()
