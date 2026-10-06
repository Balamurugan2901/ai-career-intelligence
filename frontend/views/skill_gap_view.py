import streamlit as st
from typing import Dict, Any, Optional


def render_skill_gap_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders Skill Gap Analysis & Priority Matrix page."""
    st.markdown('<div class="hero-title">Skill Gap Analysis & Priority Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Deterministic gap identification with prerequisite dependency order and effort estimates</div>', unsafe_allow_html=True)

    if not full_analysis or "skill_gap_analysis" not in full_analysis:
        st.info("No skill gap analysis loaded. Upload a resume or select a demo candidate to view gaps.")
        return

    gap_data = full_analysis.get("skill_gap_analysis", {})
    target_role = gap_data.get("target_role", full_analysis.get("target_role", "Target Role"))
    gaps = gap_data.get("gaps", [])

    st.markdown(f"### Focus Target Role: <span style='color: #38BDF8;'>{target_role}</span>", unsafe_allow_html=True)

    # Summary Metrics Header
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Identified Gaps", gap_data.get("total_gaps", len(gaps)))
    with c2:
        st.metric("High Priority Gaps", gap_data.get("high_priority_count", 0))
    with c3:
        st.metric("Medium Priority Gaps", gap_data.get("medium_priority_count", 0))
    with c4:
        st.metric("Matched Strengths", gap_data.get("matched_strengths_count", 0))

    st.divider()

    sources = gap_data.get("sources", [])
    if sources:
        from frontend.styles import render_evidence_sources
        render_evidence_sources(sources, title="Evidence & Sources for Skill Gap Analysis")


    tab1, tab2 = st.tabs(["🧩 Prioritized Skill Gaps", "💪 Identified Profile Strengths"])

    with tab1:
        if not gaps:
            st.success("🎉 Excellent alignment! No major skill gaps detected for this role.")
        else:
            for item in gaps:
                skill_name = item.get("skill", "Skill")
                priority = item.get("priority", "MEDIUM").upper()
                gap_type = item.get("gap_type", "missing")
                current_lvl = item.get("current_level") or "None"
                target_lvl = item.get("target_level", "Intermediate")
                effort = item.get("estimated_learning_effort", "2-3 weeks")
                reason = item.get("reason", "")
                dependencies = item.get("dependency_skills", [])

                badge_class = "badge-high" if priority == "HIGH" else ("badge-medium" if priority == "MEDIUM" else "badge-low")

                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        <h4 style="margin-bottom: 0.2rem; color: #F8FAFC;">
                            {skill_name} <span class="badge {badge_class}">{priority} PRIORITY</span>
                        </h4>
                        <p style="color: #94A3B8; font-size: 0.9rem; margin-bottom: 0.4rem;">{reason}</p>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: right; color: #38BDF8; font-size: 0.85rem;">
                            <b>Effort:</b> {effort}
                        </div>
                        """, unsafe_allow_html=True)

                    c_a, c_b = st.columns(2)
                    with c_a:
                        st.write(f"**Level Progression:** `{current_lvl}` ➔ `{target_lvl}` ({gap_type.upper()})")
                    with c_b:
                        if dependencies:
                            st.write(f"**Prerequisites:** {', '.join([f'`{d}`' for d in dependencies])}")

                    st.divider()

    with tab2:
        st.markdown("### Profile Strengths Matched to Role")
        strengths = [g for g in gaps if g.get("gap_type") == "strength"]
        if strengths:
            for s in strengths:
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color: #34D399; margin: 0;">✅ {s.get('skill')}</h4>
                    <p style="color: #94A3B8; margin-top: 0.3rem;">{s.get('reason')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Strengths are evaluated and mapped directly in the candidate profile overview.")
