# Model Context Protocol (MCP) Infrastructure Documentation

## 1. System Overview

The **Model Context Protocol (MCP)** infrastructure provides lightweight, standard-compliant local tool capabilities to downstream agents under `backend/mcp/`. It operates deterministically in-process against local reference knowledge (`data/knowledge/` and `data/market_reference/roles.json`), returning structured data and source provenance (`source: "MCP Local Reference Provider"`).

---

## 2. Server Architecture

- **Class**: `backend.mcp.server.LocalMCPServer`
- **Design Pattern**: Native in-process registry pattern. Tools register via `@server.register_tool(name, description)`.
- **Memory Footprint**: Execution footprint is **<10 MB RAM** with tool call latency **<1 ms**.
- **Graceful Degradation**: If `MCP_ENABLED=False` or a tool encounters invalid arguments, `MCPToolResponse` returns `success=False` with error details, allowing agents to fall back cleanly to default behavior.

---

## 3. Tool Schemas

Tool requests and responses use strict Pydantic schemas defined in `backend/mcp/schemas.py`:

```python
class MCPToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

class MCPToolResponse(BaseModel):
    tool_name: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    source: str = "MCP Local Reference Provider"
```

---

## 4. Local Tool Catalog

| Tool Name | Module | Description | Parameters |
|---|---|---|---|
| `get_role_requirements` | `job_tools.py` | Fetches core requirements for tech roles | `role_name: str` |
| `search_jobs` | `job_tools.py` | Searches job descriptions by keyword & role | `keyword: str`, `role_filter: str` |
| `get_market_benchmark` | `market_tools.py` | Returns salary & demand benchmarks | `role_name: str` |
| `search_skill_dependencies` | `skill_tools.py` | Fetches prerequisite trees for skills | `skill_name: str` |
| `search_learning_resources` | `resource_tools.py` | Searches learning resource catalogs | `query: str`, `resource_type: str` |
| `search_interview_bank` | `resource_tools.py` | Searches interview questions & rubrics | `category: str`, `role: str` |

---

## 5. Provenance & Source Citation

Every tool execution automatically attaches provenance metadata:

```json
{
  "source": "MCP Local Reference Provider",
  "tool": "get_market_benchmark",
  "title": "MCP Market Benchmark for GenAI Engineer",
  "demand_level": "HIGH DEMAND"
}
```

These provenance objects are aggregated by `CareerAnalysisPipeline` into the global `evidence_sources` record for Streamlit UI transparency rendering.
