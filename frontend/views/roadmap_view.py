import streamlit as st
from typing import Dict, Any, Optional


def render_roadmap_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders Multi-Phase Learning Roadmap page."""
    st.markdown('<div class="hero-title">Personalized Multi-Phase Learning Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Ordered 6-phase progressive learning roadmap with hands-on mini projects and verification milestones</div>', unsafe_allow_html=True)

    if not full_analysis or "learning_roadmap" not in full_analysis:
        st.info("No learning roadmap loaded. Upload a resume or select a demo candidate to view roadmap.")
        return

    roadmap = full_analysis.get("learning_roadmap", {})
    target_role = roadmap.get("target_role", full_analysis.get("target_role", "Target Role"))
    phases = roadmap.get("phases", [])

    st.markdown(f"### Roadmap for Target Role: <span style='color: #38BDF8;'>{target_role}</span>", unsafe_allow_html=True)
    st.divider()

    if not phases:
        st.write("No roadmap phases generated.")
        return

    for phase in phases:
        phase_num = phase.get("phase_number", 1)
        phase_name = phase.get("phase_name", f"Phase {phase_num}")
        description = phase.get("description", "")
        duration = phase.get("estimated_duration", "2 weeks")
        items = phase.get("items", [])

        with st.expander(f"📍 Phase {phase_num}: {phase_name} ({duration})", expanded=(phase_num in [1, 2])):
            st.markdown(f"*{description}*")
            st.markdown("<br>", unsafe_allow_html=True)

            for idx, item in enumerate(items, 1):
                skill = item.get("skill", f"Skill {idx}")
                why = item.get("why_it_matters", "")
                what = item.get("what_to_learn", "")
                task = item.get("practical_task", "")
                project = item.get("mini_project", "")
                validation = item.get("validation_method", "")
                effort = item.get("estimated_effort", "5-10 hours")

                st.markdown(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #38BDF8;">{phase_num}.{idx} Master {skill}</h4>
                        <span class="badge badge-low">⏱️ {effort}</span>
                    </div>
                    <p style="color: #E2E8F0; margin-top: 0.5rem;"><b>Why it matters:</b> {why}</p>
                    <p style="color: #94A3B8;"><b>What to learn:</b> {what}</p>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 0.8rem; border-radius: 8px; border-left: 3px solid #38BDF8; margin-top: 0.5rem;">
                        <div><b>🔨 Practical Task:</b> {task}</div>
                        <div style="margin-top: 0.3rem;"><b>🚀 Mini-Project:</b> {project}</div>
                        <div style="margin-top: 0.3rem; color: #34D399;"><b>✅ Verification Method:</b> {validation}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
