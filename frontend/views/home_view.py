import streamlit as st
from typing import Dict, Any, Optional
from frontend.services.api_client import api_client


def render_home_view(full_analysis: Optional[Dict[str, Any]], is_demo_mode: bool):
    """Renders Overview / Dashboard Home page."""
    st.markdown('<div class="hero-title">Career Intelligence Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Autonomous Multi-Agent AI System for Profile Analysis, Market Fit, and Personalized Growth</div>', unsafe_allow_html=True)

    if not full_analysis:
        st.info("💡 **Welcome!** Upload a candidate resume in the **Resume Upload** tab or load sample demo analysis to get started.")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🚀 Load Sample Candidate Analysis (Demo)", use_container_width=True, type="primary"):
                try:
                    with st.spinner("Executing 7-Agent Analysis Pipeline on Sample Candidate..."):
                        demo_data = api_client.get_full_analysis(candidate_id=1)
                        st.session_state.full_analysis = demo_data
                        st.session_state.candidate_id = demo_data.get("candidate_id", 1)
                        st.session_state.target_role = demo_data.get("target_role", "GenAI Engineer")
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to fetch sample candidate data: {e}")

        with col2:
            st.markdown("""
            **What this system does:**
            - **Parses & Intelligence**: Extracts structured skills, projects & experience.
            - **Transparent Fit Scoring**: Weighted Python match calculation.
            - **Market Benchmark**: Real-time market demand benchmark.
            - **Priority Gap Matrix**: Maps prerequisite dependencies.
            - **Actionable Roadmap**: 6 progressive phases with mini-projects.
            - **Portfolio Builder**: 3 custom tailored project recommendations.
            - **Interview Prep**: Category questions & STAR frameworks.
            """)
    else:
        # Render high-level summary metrics
        profile = full_analysis.get("profile", {})
        matches = full_analysis.get("career_matches", [])
        gaps = full_analysis.get("skill_gap_analysis", {})
        target_role = full_analysis.get("target_role", "Target Role")
        exec_time = full_analysis.get("execution_time_seconds", 0.0)
        cached = full_analysis.get("cached", False)
        evidence_sources = full_analysis.get("evidence_sources", [])

        top_match = matches[0] if matches else {"role_name": target_role, "fit_score": 85.0}
        high_gaps_count = gaps.get("high_priority_count", 0)

        if cached:
            st.markdown('<span class="badge badge-cache">⚡ CACHED PIPELINE RESULT</span> <span style="color: #94A3B8; font-size: 0.85rem;">Served instantly from in-memory pipeline cache</span>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Candidate Profile</div>
                <div class="metric-value">{profile.get("name", "Candidate")}</div>
                <div class="metric-delta">{profile.get("years_of_experience", 0)} Yrs Exp</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Top Career Match</div>
                <div class="metric-value">{top_match.get("fit_score", 0):.0f}%</div>
                <div class="metric-delta">{top_match.get("role_name", "Target Role")}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">High-Priority Gaps</div>
                <div class="metric-value" style="color: #F87171;">{high_gaps_count}</div>
                <div class="metric-delta">Target: {target_role}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Evidence & Sources</div>
                <div class="metric-value" style="color: #38BDF8;">{len(evidence_sources)}</div>
                <div class="metric-delta">RAG & MCP Sources</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Evidence Sources Inspector
        from frontend.styles import render_evidence_sources
        render_evidence_sources(evidence_sources, title="Global Pipeline Execution Evidence & Provenance")


        # Immediate Actionable Next Steps Card
        st.markdown("### ⚡ Actionable Next Steps")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="glass-card">
                <h4 style="color: #38BDF8; margin-top:0;">🎯 Focus Role: {target_role}</h4>
                <p>Top missing skills required to reach target level:</p>
                {"".join([f'<span class="badge badge-high">{g["skill"]}</span>' for g in gaps.get("gaps", []) if g.get("priority") == "HIGH"][:5])}
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("""
            <div class="glass-card">
                <h4 style="color: #34D399; margin-top:0;">🚀 Recommended Next Action</h4>
                <p>Proceed to the <b>Learning Roadmap</b> or <b>Project Recommendations</b> tab to begin building projects that directly eliminate identified skill gaps.</p>
            </div>
            """, unsafe_allow_html=True)

    # 7-Agent Architecture Flow Diagram / Info
    st.divider()
    with st.expander("ℹ️ How this Analysis Works (7-Agent Pipeline Architecture)", expanded=False):
        st.markdown("""
        ```mermaid
        graph TD
            A[Resume Parser] --> B[Resume Intelligence Agent]
            B --> C[Career Matching Agent]
            C --> D[Market Intelligence Agent]
            D --> E[Skill Gap Agent]
            E --> F[Learning Roadmap Agent]
            F --> G[Project Recommendation Agent]
            G --> H[Interview Preparation Agent]
        ```
        - **Data Lifecycle**: Raw text is parsed once by the Resume Parser. Intermediate structured Pydantic schemas are passed down the pipeline, conserving LLM tokens and avoiding redundant raw text re-processing.
        - **Execution State**: Tracks start, progress, duration, and status transitions (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`) in SQLite database records.
        """)
