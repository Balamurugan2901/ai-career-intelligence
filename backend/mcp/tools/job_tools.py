import json
import os
from typing import Optional, List, Dict, Any

from backend.mcp.schemas import (
    RoleRequirementsQuery,
    RoleRequirementsResult,
    JobSearchQuery,
    JobSearchResult,
)
from backend.services.market.market_service import market_service
from backend.utils.logger import logger


def get_role_requirements(query: RoleRequirementsQuery) -> RoleRequirementsResult:
    """
    MCP Tool: Retrieves structured requirements, responsibilities, and skill profiles for a target role.
    """
    role_name = query.role_name.strip()
    logger.info(f"MCP job_tool get_role_requirements called for '{role_name}'")

    # 1. Attempt to load from data/knowledge/job_descriptions/
    knowledge_dir = "data/knowledge/job_descriptions"
    if os.path.exists(knowledge_dir):
        for fname in os.listdir(knowledge_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(knowledge_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    meta = data.get("metadata", {})
                    if meta.get("role", "").lower() == role_name.lower() or meta.get("title", "").lower() == role_name.lower():
                        content = data.get("content", "")
                        lines = [l.strip() for l in content.split("\n") if l.strip()]
                        summary = lines[0] if lines else f"Requirements for {role_name}"
                        return RoleRequirementsResult(
                            role_name=role_name,
                            role_title=meta.get("title", role_name),
                            summary=summary,
                            responsibilities=[l.replace("- ", "") for l in lines if l.startswith("- Design") or l.startswith("- Collaborate") or l.startswith("- Build")],
                            required_skills=[l.replace("- Primary Languages: ", "").replace("- Essential Tools & Frameworks: ", "") for l in lines if "Languages:" in l or "Tools" in l],
                            qualifications=[l.replace("- ", "") for l in lines if "degree" in l.lower() or "portfolio" in l.lower()],
                            source="MCP Local Reference Provider",
                        )
                except Exception as e:
                    logger.warning(f"Error reading knowledge doc '{fname}': {e}")

    # 2. Fallback to market_service / roles.json
    mkt = market_service.get_role_demand(role_name)
    return RoleRequirementsResult(
        role_name=mkt.get("role_name", role_name),
        role_title=f"{mkt.get('role_name', role_name)} Position",
        summary=mkt.get("salary_trend_summary", f"Core technical requirements and responsibilities for {role_name}."),
        responsibilities=mkt.get("key_responsibilities", []),
        required_skills=mkt.get("top_required_skills", []),
        qualifications=["Bachelor's or Master's in Computer Science / Data Science or equivalent practical experience."],
        source="MCP Local Reference Provider",
    )


def search_jobs(query: JobSearchQuery) -> JobSearchResult:
    """
    MCP Tool: Searches curated job benchmarks matching keyword and optional role filter.
    """
    kw = query.keyword.strip().lower()
    role_filter = query.role_name.strip().lower() if query.role_name else None
    logger.info(f"MCP job_tool search_jobs called with keyword='{kw}', role_filter='{role_filter}'")

    matches = []
    # Query market_service roles dictionary
    all_roles = market_service.get_all_roles_demand()
    for role_name, data in all_roles.items():

        if role_filter and role_filter not in role_name.lower():
            continue

        # Check keyword in role_name, skills, or responsibilities
        skills_str = " ".join(data.get("top_required_skills", []) + data.get("tools_and_frameworks", [])).lower()
        resp_str = " ".join(data.get("key_responsibilities", [])).lower()

        if kw in role_name.lower() or kw in skills_str or kw in resp_str:
            matches.append({
                "role_name": role_name,
                "demand_level": data.get("demand_level", "HIGH DEMAND"),
                "matched_skills": [s for s in data.get("top_required_skills", []) if kw in s.lower()] or data.get("top_required_skills", [])[:3],
                "key_responsibilities": data.get("key_responsibilities", [])[:2],
            })

    return JobSearchResult(
        keyword=query.keyword,
        total_matches=len(matches),
        matches=matches,
        source="MCP Local Reference Provider",
    )
