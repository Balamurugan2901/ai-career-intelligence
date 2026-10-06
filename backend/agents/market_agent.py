from typing import List, Optional, Dict, Any

from backend.config import settings
from backend.prompts.market.contextualize import (
    MARKET_CONTEXT_SYSTEM_INSTRUCTION,
    MARKET_CONTEXT_PROMPT_TEMPLATE,
)
from backend.mcp.server import mcp_server
from backend.rag.retriever import rag_retriever
from backend.schemas.market import MarketRoleDemand

from backend.services.llm.llm_service import LLMService, llm_service
from backend.services.market.market_service import MarketService, market_service
from backend.utils.logger import logger


class MarketIntelligenceAgent:
    """
    Agent 3: Market Intelligence Agent.
    Responsible for evaluating industry demand, skill requirements, emerging tech trends,
    responsibilities, and RAG domain knowledge for target career paths.
    """

    def __init__(
        self,
        llm_svc: Optional[LLMService] = None,
        mkt_svc: Optional[MarketService] = None,
    ):
        self.llm_service = llm_svc or llm_service
        self.market_service = mkt_svc or market_service

    def analyze_single_role(self, role_name: str) -> MarketRoleDemand:
        """Analyzes market demand data and RAG context for a single target role."""
        raw_data = self.market_service.get_role_demand(role_name)

        # Retrieve RAG domain context
        rag_results = rag_retriever.retrieve(query=role_name, document_type="job_description")
        context_text, sources = rag_retriever.format_context_and_sources(rag_results)
        rag_ctx_str = f"Reference Knowledge Context:\n{context_text}" if context_text else ""

        # Invoke MCP Tool
        if settings.MCP_ENABLED:
            mcp_res = mcp_server.call_tool("get_market_benchmark", {"role_name": role_name})
            if mcp_res.success and mcp_res.data:
                sources.append({
                    "source": mcp_res.source,
                    "tool": mcp_res.tool_name,
                    "title": f"MCP Market Benchmark for {role_name}",
                    "demand_level": mcp_res.data.get("demand_level"),
                })

        if settings.is_demo_mode():
            demand = MarketRoleDemand.model_validate(raw_data)
            demand.sources = sources
            return demand

        try:
            prompt = MARKET_CONTEXT_PROMPT_TEMPLATE.format(
                role_name=role_name,
                reference_data_json=raw_data,
                rag_context=rag_ctx_str,
            )
            demand = self.llm_service.generate_json(
                prompt=prompt,
                schema=MarketRoleDemand,
                system_instruction=MARKET_CONTEXT_SYSTEM_INSTRUCTION,
            )
            demand.sources = sources
            return demand
        except Exception as e:
            logger.warning(f"MarketIntelligenceAgent API call failed for '{role_name}': {e}. Returning reference data.")
            demand = MarketRoleDemand.model_validate(raw_data)
            demand.sources = sources
            return demand


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

