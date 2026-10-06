from typing import Callable, Dict, List, Optional, Type, Any
from pydantic import BaseModel, ValidationError

from backend.config import settings
from backend.mcp.schemas import (
    MCPToolDefinition,
    MCPToolCall,
    MCPToolResult,
    RoleRequirementsQuery,
    JobSearchQuery,
    MarketBenchmarkQuery,
    SkillDependencyQuery,
    LearningResourcesQuery,
    InterviewQuestionsQuery,
)
from backend.mcp.tools import (
    get_role_requirements,
    search_jobs,
    get_market_benchmark,
    search_skill_dependencies,
    search_learning_resources,
    search_interview_bank,
)
from backend.utils.logger import logger


class LocalMCPServer:
    """
    Lightweight, Native Model Context Protocol (MCP) Server.
    Provides standard tool registry, parameter validation, and execution for local reference tools.
    """

    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register_tool(
        self,
        name: str,
        description: str,
        input_model: Type[BaseModel],
        func: Callable,
    ):
        """Registers a tool with description, Pydantic input schema, and handler function."""
        params_schema = input_model.model_json_schema()
        definition = MCPToolDefinition(
            name=name,
            description=description,
            parameters=params_schema,
        )

        self._registry[name] = {
            "definition": definition,
            "input_model": input_model,
            "func": func,
        }
        logger.info(f"LocalMCPServer registered tool: '{name}'")

    def _register_default_tools(self):
        """Registers all built-in local MCP reference tools."""
        self.register_tool(
            name="get_role_requirements",
            description="Retrieves structured requirements, responsibilities, and skill profiles for a target role.",
            input_model=RoleRequirementsQuery,
            func=get_role_requirements,
        )
        self.register_tool(
            name="search_jobs",
            description="Searches curated job benchmarks matching keyword and optional role filter.",
            input_model=JobSearchQuery,
            func=search_jobs,
        )
        self.register_tool(
            name="get_market_benchmark",
            description="Retrieves industry market demand benchmarks, salary trends, and tech stack expectations.",
            input_model=MarketBenchmarkQuery,
            func=get_market_benchmark,
        )
        self.register_tool(
            name="search_skill_dependencies",
            description="Retrieves canonical prerequisite chains and dependency topics for a target technical skill.",
            input_model=SkillDependencyQuery,
            func=search_skill_dependencies,
        )
        self.register_tool(
            name="search_learning_resources",
            description="Searches curated learning resources, tutorials, documentation, and courses.",
            input_model=LearningResourcesQuery,
            func=search_learning_resources,
        )
        self.register_tool(
            name="search_interview_bank",
            description="Fetches technical and behavioral interview preparation questions with evaluation rubrics.",
            input_model=InterviewQuestionsQuery,
            func=search_interview_bank,
        )

    def list_tools(self) -> List[MCPToolDefinition]:
        """Returns list of all registered MCP tool definitions."""
        return [item["definition"] for item in self._registry.values()]

    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> MCPToolResult:
        """
        Executes an MCP tool by name with validated arguments.
        Ensures robust error handling and graceful degradation on invalid tool or parameters.
        """
        if not settings.MCP_ENABLED:
            logger.info("MCP server is disabled in configuration settings.")
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                error="MCP server is disabled in configuration settings.",
                source="MCP Local Reference Provider",
            )

        if tool_name not in self._registry:
            logger.warning(f"MCP tool call failed: Unknown tool '{tool_name}'.")
            available = list(self._registry.keys())
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Unknown tool '{tool_name}'. Available tools: {available}",
                source="MCP Local Reference Provider",
            )

        tool_entry = self._registry[tool_name]
        input_model: Type[BaseModel] = tool_entry["input_model"]
        func: Callable = tool_entry["func"]
        arguments = arguments or {}

        try:
            # 1. Parameter validation using Pydantic
            validated_query = input_model.model_validate(arguments)

            # 2. Tool function execution
            raw_result = func(validated_query)

            # Serialize output model or payload to dict if Pydantic model
            data_payload = raw_result.model_dump() if hasattr(raw_result, "model_dump") else raw_result

            logger.info(f"LocalMCPServer successfully executed tool '{tool_name}'")
            return MCPToolResult(
                tool_name=tool_name,
                success=True,
                data=data_payload,
                source="MCP Local Reference Provider",
            )

        except ValidationError as ve:
            logger.warning(f"Parameter validation failed for tool '{tool_name}': {ve}")
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Invalid arguments for tool '{tool_name}': {ve}",
                source="MCP Local Reference Provider",
            )
        except Exception as e:
            logger.error(f"Error executing MCP tool '{tool_name}': {e}")
            return MCPToolResult(
                tool_name=tool_name,
                success=False,
                error=f"Tool execution failed: {e}",
                source="MCP Local Reference Provider",
            )


# Singleton MCP Server instance
mcp_server = LocalMCPServer()
