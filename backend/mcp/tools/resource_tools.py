import json
import os
from typing import Optional, List, Dict, Any

from backend.mcp.schemas import (
    LearningResourcesQuery,
    LearningResourcesResult,
    InterviewQuestionsQuery,
    InterviewQuestionsResult,
)
from backend.utils.logger import logger


def search_learning_resources(query: LearningResourcesQuery) -> LearningResourcesResult:
    """
    MCP Tool: Searches curated learning resources, tutorials, documentation, and courses.
    """
    s_name = query.skill_name.strip()
    s_key = s_name.lower()
    logger.info(f"MCP resource_tool search_learning_resources called for '{s_name}'")

    resources = []
    lr_dir = "data/knowledge/learning_resources"
    if os.path.exists(lr_dir):
        for fname in os.listdir(lr_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(lr_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    meta = data.get("metadata", {})
                    content = data.get("content", "")
                    if s_key in meta.get("title", "").lower() or s_key in content.lower():
                        resources.append({
                            "title": meta.get("title", s_name),
                            "type": meta.get("document_type", "learning_resource"),
                            "target_role": meta.get("role", "General"),
                            "summary": content,
                        })
                except Exception as e:
                    logger.warning(f"Error parsing resource doc '{fname}': {e}")

    if not resources:
        # Default fallback resource entries
        resources = [
            {
                "title": f"Official {s_name} Documentation & Tutorials",
                "type": "Official Documentation",
                "target_role": "All Tech Roles",
                "summary": f"Comprehensive guide to learning {s_name} from fundamentals to production best practices.",
            },
            {
                "title": f"Applied {s_name} Hands-On Portfolio Project Guide",
                "type": "Interactive Guide",
                "target_role": "Software & AI Engineers",
                "summary": f"Build an end-to-end practical project mastering {s_name} with automated tests.",
            },
        ]

    return LearningResourcesResult(
        skill_name=s_name,
        total_found=len(resources),
        resources=resources,
        source="MCP Local Reference Provider",
    )


def search_interview_bank(query: InterviewQuestionsQuery) -> InterviewQuestionsResult:
    """
    MCP Tool: Fetches technical and behavioral interview preparation questions with evaluation rubrics.
    """
    category = query.category.strip() if query.category else "Technical Questions"
    role_filter = query.role_name.strip().lower() if query.role_name else None
    logger.info(f"MCP resource_tool search_interview_bank called for category='{category}', role='{role_filter}'")

    questions = []
    iq_dir = "data/knowledge/interview_questions"
    if os.path.exists(iq_dir):
        for fname in os.listdir(iq_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(iq_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    meta = data.get("metadata", {})
                    content = data.get("content", "")
                    if not role_filter or role_filter in meta.get("role", "").lower():
                        questions.append({
                            "title": meta.get("title", "Interview Questions"),
                            "category": category,
                            "role": meta.get("role", "General"),
                            "question_text": content,
                        })
                except Exception as e:
                    logger.warning(f"Error parsing interview doc '{fname}': {e}")

    if not questions:
        # Default structured fallback questions
        questions = [
            {
                "question": f"Explain key architectural trade-offs when implementing scalable systems for {query.role_name or 'software engineer'} roles.",
                "category": category,
                "difficulty": "Senior",
                "evaluation_rubric": "Evaluates candidate's understanding of latency, throughput, and system failure modes.",
            },
            {
                "question": f"Walk through a challenging debugging scenario in your recent project and describe your troubleshooting process.",
                "category": category,
                "difficulty": "Mid-Level",
                "evaluation_rubric": "Assesses systematic problem-solving skills and communication under pressure.",
            },
        ]

    return InterviewQuestionsResult(
        category=category,
        total_questions=len(questions),
        questions=questions,
        source="MCP Local Reference Provider",
    )
