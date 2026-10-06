import streamlit as st
from typing import Dict, Any, Optional


def render_projects_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders Portfolio Project Recommendations page."""
    st.markdown('<div class="hero-title">Portfolio Project Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">3 Progressive project blueprints tailored to candidate skill gaps and target role requirements</div>', unsafe_allow_html=True)

    if not full_analysis or "project_recommendations" not in full_analysis:
        st.info("No project recommendations loaded. Upload a resume or select a demo candidate to view project recommendations.")
        return

    projects_data = full_analysis.get("project_recommendations", {})
    target_role = projects_data.get("target_role", full_analysis.get("target_role", "Target Role"))
    projects = projects_data.get("projects", [])

    st.markdown(f"### Recommended Projects for: <span style='color: #38BDF8;'>{target_role}</span>", unsafe_allow_html=True)

    sources = projects_data.get("sources", [])
    if sources:
        from frontend.styles import render_evidence_sources
        render_evidence_sources(sources, title="Evidence & Sources for Project Recommendations")

    st.divider()

    if not projects:
        st.write("No projects recommended.")
        return

    for proj in projects:
        title = proj.get("project_title", "Portfolio Project")
        difficulty = proj.get("difficulty", "Intermediate").upper()
        problem = proj.get("problem_statement", "")
        why = proj.get("why_this_project", "")
        skills = proj.get("skills_covered", [])
        features = proj.get("expected_features", [])
        tech_stack = proj.get("technology_stack", [])
        outcomes = proj.get("learning_outcomes", [])
        resume_val = proj.get("resume_value", "")
        extensions = proj.get("suggested_extensions", [])

        badge_class = "badge-low" if "BEGINNER" in difficulty else ("badge-medium" if "INTERMEDIATE" in difficulty else "badge-high")

        with st.container():
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #38BDF8;">{title}</h3>
                    <span class="badge {badge_class}">{difficulty} LEVEL</span>
                </div>
                <p style="color: #E2E8F0; margin-top: 0.6rem;"><b>Problem Statement:</b> {problem}</p>
                <div style="background: rgba(56, 189, 248, 0.08); border-left: 3px solid #38BDF8; padding: 0.6rem 0.8rem; border-radius: 6px; margin: 0.5rem 0;">
                    <b>🎯 Why this targets your gap:</b> {why}
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Core Capabilities / Features:**")
                for f in features:
                    st.markdown(f"- {f}")

                st.markdown("**Skills Mastery Covered:**")
                pills = "".join([f'<span class="skill-pill">{s}</span>' for s in skills])
                st.markdown(pills, unsafe_allow_html=True)

            with col2:
                st.markdown("**Recommended Technology Stack:**")
                tech_pills = "".join([f'<span class="skill-pill skill-pill-strength">{t}</span>' for t in tech_stack])
                st.markdown(tech_pills, unsafe_allow_html=True)

                st.markdown("<br>**💼 Resume Talking Points & Value:**", unsafe_allow_html=True)
                st.info(resume_val)

            with st.expander("🚀 Next-Level Suggested Extensions & Learning Outcomes"):
                st.markdown("**Learning Outcomes:**")
                for o in outcomes:
                    st.markdown(f"- {o}")
                
                if extensions:
                    st.markdown("<br>**Suggested Advanced Extensions:**", unsafe_allow_html=True)
                    for ext in extensions:
                        st.markdown(f"- {ext}")

            st.divider()
