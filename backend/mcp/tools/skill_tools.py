import json
import os
from backend.mcp.schemas import SkillDependencyQuery, SkillDependencyResult
from backend.utils.logger import logger


# Default prerequisite taxonomy fallback
DEFAULT_PREREQUISITES_TAXONOMY = {
    "python": {
        "canonical": "Python Programming",
        "prerequisites": ["Basic Programming Concepts"],
        "core_topics": ["Data Structures", "OOP", "Async Processing", "Virtual Environments"],
        "target_roles": ["AI Engineer", "Backend Developer", "Data Scientist", "GenAI Engineer"],
        "description": "Foundational programming language for modern AI, data analytics, and backend microservices.",
    },
    "pytorch": {
        "canonical": "PyTorch Framework",
        "prerequisites": ["Python", "Linear Algebra", "Calculus"],
        "core_topics": ["Tensors", "Autograd", "Neural Network Modules", "CUDA Optimization"],
        "target_roles": ["AI Engineer", "ML Engineer", "Computer Vision Engineer"],
        "description": "Leading open-source deep learning framework for research and model deployment.",
    },
    "rag": {
        "canonical": "Retrieval-Augmented Generation (RAG)",
        "prerequisites": ["Python", "Large Language Models", "Vector Databases"],
        "core_topics": ["Chunking Strategies", "Embeddings", "Vector Search", "Reranking", "Source Citation"],
        "target_roles": ["GenAI Engineer", "AI Engineer"],
        "description": "Architectural pattern grounding LLM generation on external vector knowledge bases.",
    },
    "sql": {
        "canonical": "SQL & Relational Databases",
        "prerequisites": ["Database Fundamentals"],
        "core_topics": ["Joins", "Aggregations", "CTEs", "Window Functions", "Query Optimization"],
        "target_roles": ["Data Analyst", "Data Scientist", "Backend Developer"],
        "description": "Industry-standard language for relational data querying, aggregation, and analytics.",
    },
    "fastapi": {
        "canonical": "FastAPI Web Framework",
        "prerequisites": ["Python", "REST APIs", "Async I/O"],
        "core_topics": ["Pydantic Schemas", "Dependency Injection", "OpenAPI", "Async Routes"],
        "target_roles": ["Backend Developer", "AI Engineer", "GenAI Engineer"],
        "description": "Modern, high-performance Python web framework for building async RESTful APIs.",
    },
    "docker": {
        "canonical": "Docker Containerization",
        "prerequisites": ["Linux Shell Commands"],
        "core_topics": ["Dockerfiles", "Multi-stage Builds", "Container Networking", "Volumes"],
        "target_roles": ["MLOps Engineer", "Backend Developer", "AI Engineer"],
        "description": "Container virtualization platform ensuring consistent application execution across environments.",
    },
}


def search_skill_dependencies(query: SkillDependencyQuery) -> SkillDependencyResult:
    """
    MCP Tool: Retrieves canonical prerequisite chains and dependency topics for a target technical skill.
    """
    s_name = query.skill_name.strip()
    s_key = s_name.lower()
    logger.info(f"MCP skill_tool search_skill_dependencies called for '{s_name}'")

    # 1. Attempt reading from data/knowledge/skills/
    skills_dir = "data/knowledge/skills"
    if os.path.exists(skills_dir):
        for fname in os.listdir(skills_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(skills_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    meta = data.get("metadata", {})
                    content = data.get("content", "")
                    if s_key in meta.get("title", "").lower() or s_key in content.lower():
                        lines = content.split(".")
                        prereqs = []
                        topics = []
                        for part in lines:
                            if "Prerequisites:" in part:
                                prereqs = [p.strip() for p in part.replace("Prerequisites:", "").split(",")]
                            elif "Core Topics:" in part:
                                topics = [t.strip() for t in part.replace("Core Topics:", "").split(",")]

                        return SkillDependencyResult(
                            skill_name=s_name,
                            canonical_skill=meta.get("title", s_name),
                            prerequisites=prereqs or ["Python"],
                            core_topics=topics or ["Foundational Concepts"],
                            target_roles=[meta.get("role", "AI Engineer")],
                            description=content,
                            source="MCP Local Reference Provider",
                        )
                except Exception as e:
                    logger.warning(f"Error parsing skill doc '{fname}': {e}")

    # 2. Check fallback taxonomy
    for key, tax in DEFAULT_PREREQUISITES_TAXONOMY.items():
        if key in s_key or s_key in key:
            return SkillDependencyResult(
                skill_name=s_name,
                canonical_skill=tax["canonical"],
                prerequisites=tax["prerequisites"],
                core_topics=tax["core_topics"],
                target_roles=tax["target_roles"],
                description=tax["description"],
                source="MCP Local Reference Provider",
            )

    # Generic default result
    return SkillDependencyResult(
        skill_name=s_name,
        canonical_skill=s_name,
        prerequisites=["Python", "Computer Science Fundamentals"],
        core_topics=["Core Syntax", "Practical Implementation", "Testing"],
        target_roles=["Software Developer", "AI Engineer"],
        description=f"Technical skill prerequisite and topic breakdown for {s_name}.",
        source="MCP Local Reference Provider",
    )
