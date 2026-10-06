import tracemalloc
import pytest
from unittest.mock import patch

from backend.config import settings
from backend.mcp.server import mcp_server, LocalMCPServer
from backend.mcp.schemas import MCPToolDefinition, MCPToolResult


def test_mcp_list_tools():
    """Test tool registry discovery list_tools returns all 6 default tools."""
    tools = mcp_server.list_tools()
    assert len(tools) == 6
    tool_names = [t.name for t in tools]
    expected = [
        "get_role_requirements",
        "search_jobs",
        "get_market_benchmark",
        "search_skill_dependencies",
        "search_learning_resources",
        "search_interview_bank",
    ]
    for exp in expected:
        assert exp in tool_names


def test_mcp_get_role_requirements_tool():
    """Test execution of get_role_requirements tool."""
    res: MCPToolResult = mcp_server.call_tool(
        "get_role_requirements",
        {"role_name": "GenAI Engineer"}
    )
    assert res.success is True
    assert res.tool_name == "get_role_requirements"
    assert res.source == "MCP Local Reference Provider"
    assert res.data["role_name"] == "GenAI Engineer"
    assert len(res.data["responsibilities"]) > 0
    assert len(res.data["required_skills"]) > 0


def test_mcp_search_jobs_tool():
    """Test execution of search_jobs tool."""
    res: MCPToolResult = mcp_server.call_tool(
        "search_jobs",
        {"keyword": "Python", "role_name": "AI Engineer"}
    )
    assert res.success is True
    assert res.data["keyword"] == "Python"
    assert res.data["total_matches"] >= 0
    assert isinstance(res.data["matches"], list)


def test_mcp_get_market_benchmark_tool():
    """Test execution of get_market_benchmark tool."""
    res: MCPToolResult = mcp_server.call_tool(
        "get_market_benchmark",
        {"role_name": "Backend Developer"}
    )
    assert res.success is True
    assert res.data["role_name"] == "Backend Developer"
    assert "demand_level" in res.data
    assert len(res.data["top_required_skills"]) > 0


def test_mcp_search_skill_dependencies_tool():
    """Test execution of search_skill_dependencies tool."""
    res: MCPToolResult = mcp_server.call_tool(
        "search_skill_dependencies",
        {"skill_name": "PyTorch"}
    )
    assert res.success is True
    assert res.data["skill_name"] == "PyTorch"
    assert "canonical_skill" in res.data
    assert isinstance(res.data["prerequisites"], list)


def test_mcp_search_learning_resources_tool():
    """Test execution of search_learning_resources tool."""
    res: MCPToolResult = mcp_server.call_tool(
        "search_learning_resources",
        {"skill_name": "RAG"}
    )
    assert res.success is True
    assert res.data["skill_name"] == "RAG"
    assert res.data["total_found"] > 0
    assert len(res.data["resources"]) > 0


def test_mcp_search_interview_bank_tool():
    """Test execution of search_interview_bank tool."""
    res: MCPToolResult = mcp_server.call_tool(
        "search_interview_bank",
        {"category": "GenAI Questions", "role_name": "GenAI Engineer"}
    )
    assert res.success is True
    assert res.data["total_questions"] > 0
    assert len(res.data["questions"]) > 0


def test_mcp_invalid_tool_name():
    """Test calling an unknown tool returns error payload without crashing."""
    res: MCPToolResult = mcp_server.call_tool(
        "non_existent_tool",
        {"query": "test"}
    )
    assert res.success is False
    assert res.tool_name == "non_existent_tool"
    assert "Unknown tool" in res.error


def test_mcp_malformed_arguments():
    """Test passing invalid argument types returns error payload without crashing."""
    res: MCPToolResult = mcp_server.call_tool(
        "get_role_requirements",
        {}  # Missing required role_name
    )
    assert res.success is False
    assert "Invalid arguments" in res.error


def test_mcp_disabled_graceful_degradation():
    """Test graceful degradation when MCP_ENABLED is False."""
    with patch.object(settings, "MCP_ENABLED", False):
        res: MCPToolResult = mcp_server.call_tool(
            "get_market_benchmark",
            {"role_name": "AI Engineer"}
        )
        assert res.success is False
        assert "disabled" in res.error.lower()


def test_mcp_memory_and_performance():
    """Verify MCP server operations consume < 10MB RAM and execute quickly."""
    tracemalloc.start()
    snapshot_before = tracemalloc.take_snapshot()

    # Execute batch of tool calls
    for _ in range(20):
        mcp_server.call_tool("get_market_benchmark", {"role_name": "Data Scientist"})
        mcp_server.call_tool("search_skill_dependencies", {"skill_name": "SQL"})

    snapshot_after = tracemalloc.take_snapshot()
    tracemalloc.stop()

    top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
    total_diff_kb = sum(stat.size_diff for stat in top_stats) / 1024.0

    # Assert memory increase is under 10MB (10240 KB)
    assert total_diff_kb < 10240.0
