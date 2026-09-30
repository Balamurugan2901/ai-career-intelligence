import streamlit as st
from typing import Dict, Any, Optional
from frontend.services.api_client import api_client


def render_career_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders Heuristic Career Match page."""
    st.markdown('<div class="hero-title">Career Path Intelligence & Transparent Fit Scoring</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Deterministic heuristic evaluation comparing candidate profile against target roles</div>', unsafe_allow_html=True)

    st.info("ℹ️ **Transparent Metric Note:** 'Profile Fit Score' represents deterministic skill, experience, education, and project alignment. It is a profile match score, **not** an employment or hiring probability.")

    if not full_analysis or "career_matches" not in full_analysis:
        st.info("No career analysis loaded. Upload a resume or select a demo candidate to view career matches.")
        return

    matches = full_analysis.get("career_matches", [])
    current_target = full_analysis.get("target_role", "")

    st.markdown(f"### Current Active Focus Role: <span style='color: #38BDF8;'>{current_target}</span>", unsafe_allow_html=True)
    st.divider()

    for idx, match in enumerate(matches, 1):
        role_name = match.get("role_name", f"Role #{idx}")
        fit_score = match.get("fit_score", 0.0)
        reasoning = match.get("reasoning", "")
        matching_skills = match.get("matching_skills", [])
        missing_skills = match.get("missing_skills", [])
        recommended_next = match.get("recommended_next_step", "")

        is_selected = (role_name.lower() == current_target.lower())

        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <h3 style="margin-bottom: 0.2rem; color: {'#38BDF8' if is_selected else '#F8FAFC'};">
                    #{idx} {role_name} {'<span class="badge badge-fit">ACTIVE TARGET</span>' if is_selected else ''}
                </h3>
                <p style="color: #94A3B8; margin-bottom: 0.8rem;">{reasoning}</p>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-box" style="padding: 0.8rem;">
                    <div class="metric-label">Profile Fit Score</div>
                    <div class="metric-value">{fit_score:.0f}%</div>
                </div>
                """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Matching Candidate Skills:**")
                if matching_skills:
                    pills = "".join([f'<span class="skill-pill skill-pill-strength">{s}</span>' for s in matching_skills])
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.write("None identified")

            with c2:
                st.markdown("**Missing / Required Skills:**")
                if missing_skills:
                    pills = "".join([f'<span class="skill-pill skill-pill-gap">{s}</span>' for s in missing_skills])
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.write("No major gaps")

            st.markdown(f"**Recommended Next Step:** {recommended_next}")

            # Role Selection Button
            if not is_selected:
                if st.button(f"🎯 Set '{role_name}' as Active Target Role", key=f"select_role_{idx}"):
                    try:
                        candidate_id = full_analysis.get("candidate_id", 1)
                        with st.spinner(f"Re-running downstream agents for target role: '{role_name}'..."):
                            # Re-run pipeline with chosen role
                            res = api_client.start_pipeline_analysis(candidate_id=candidate_id, target_role=role_name)
                            updated_analysis = api_client.get_full_analysis(candidate_id=candidate_id)
                            st.session_state.full_analysis = updated_analysis
                            st.session_state.target_role = role_name
                            st.success(f"Updated active focus role to '{role_name}'!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update focus role: {e}")

            st.divider()
