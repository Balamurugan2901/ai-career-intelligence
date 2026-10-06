from backend.mcp.schemas import MarketBenchmarkQuery, MarketBenchmarkResult
from backend.services.market.market_service import market_service
from backend.utils.logger import logger


def get_market_benchmark(query: MarketBenchmarkQuery) -> MarketBenchmarkResult:
    """
    MCP Tool: Retrieves industry market demand benchmarks, salary trends, and tech stack expectations.
    """
    role_name = query.role_name.strip()
    logger.info(f"MCP market_tool get_market_benchmark called for '{role_name}'")

    raw_data = market_service.get_role_demand(role_name)

    return MarketBenchmarkResult(
        role_name=raw_data.get("role_name", role_name),
        demand_level=raw_data.get("demand_level", "HIGH DEMAND"),
        top_required_skills=raw_data.get("top_required_skills", []),
        emerging_skills=raw_data.get("emerging_skills", []),
        tools_and_frameworks=raw_data.get("tools_and_frameworks", []),
        cloud_technologies=raw_data.get("cloud_technologies", []),
        key_responsibilities=raw_data.get("key_responsibilities", []),
        salary_trend_summary=raw_data.get("salary_trend_summary", "Strong market demand across technology sectors."),
        data_source="MCP Local Reference Provider",
    )
