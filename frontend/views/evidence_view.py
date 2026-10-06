import streamlit as st
from typing import Dict, Any, Optional
from frontend.styles import render_evidence_sources


def render_evidence_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders dedicated RAG Evidence & Source Traceability Dashboard."""
    st.markdown('<div class="hero-title">RAG Evidence & Source Traceability</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Comprehensive provenance record of all RAG knowledge base retrievals, MCP local tool executions, and pipeline caching state</div>', unsafe_allow_html=True)

    if not full_analysis:
        st.info("No analysis loaded. Upload a candidate resume or select a demo candidate to view evidence and provenance records.")
        return

    evidence_sources = full_analysis.get("evidence_sources", [])
    cached = full_analysis.get("cached", False)
    target_role = full_analysis.get("target_role", "Target Role")
    exec_time = full_analysis.get("execution_time_seconds", 0.0)

    # Cache & Execution Performance Metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Pipeline Cache Status", "⚡ CACHED" if cached else "🔄 LIVE RUN")
    with c2:
        st.metric("Total Evidence Consulted", f"{len(evidence_sources)} Sources")
    with c3:
        st.metric("Target Focus Role", target_role)

    st.divider()

    if cached:
        st.info("⚡ **Pipeline Served From Cache:** This full candidate analysis was retrieved instantly from the local pipeline memory cache key, avoiding redundant vector retrievals and LLM invocations.")

    st.markdown("### 📜 Aggregated Traceability Record")
    st.caption("The breakdown below lists every RAG reference chunk retrieved and every MCP tool executed by the downstream agents during analysis.")

    if not evidence_sources:
        st.warning("No explicit evidence sources returned in this analysis run.")
        return

    # Categorize into RAG vs MCP vs Reference
    rag_sources = [s for s in evidence_sources if "rag" in str(s.get("source", "")).lower() or "chunk" in str(s.get("document_type", "")).lower()]
    mcp_sources = [s for s in evidence_sources if "mcp" in str(s.get("source", "")).lower() or "tool" in str(s.get("document_type", "")).lower()]
    ref_sources = [s for s in evidence_sources if s not in rag_sources and s not in mcp_sources]

    t1, t2, t3, t4 = st.tabs([
        f"All Sources ({len(evidence_sources)})",
        f"📚 RAG Context ({len(rag_sources)})",
        f"🛠️ MCP Tools ({len(mcp_sources)})",
        f"📖 Reference Data ({len(ref_sources)})"
    ])

    with t1:
        render_evidence_sources(evidence_sources, title="All Consulted Evidence Sources")

    with t2:
        render_evidence_sources(rag_sources, title="Retrieved Knowledge Base Vector Chunks")

    with t3:
        render_evidence_sources(mcp_sources, title="Local Model Context Protocol (MCP) Tool Invocations")

    with t4:
        render_evidence_sources(ref_sources, title="Curated Reference & Deterministic Data")
