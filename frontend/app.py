import os
import sys
from pathlib import Path
import streamlit as st

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.services.api_client import api_client
from frontend.styles import apply_custom_styles
from frontend.views.home_view import render_home_view
from frontend.views.resume_view import render_resume_view
from frontend.views.career_view import render_career_view
from frontend.views.market_view import render_market_view
from frontend.views.skill_gap_view import render_skill_gap_view
from frontend.views.roadmap_view import render_roadmap_view
from frontend.views.projects_view import render_projects_view
from frontend.views.interview_view import render_interview_view
from frontend.views.status_view import render_status_view

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Career Intelligence & Growth Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Dark Glassmorphism CSS Design System
apply_custom_styles()


def init_session_state():
    """Initializes persistent application session variables."""
    if "candidate_id" not in st.session_state:
        st.session_state.candidate_id = None
    if "analysis_id" not in st.session_state:
        st.session_state.analysis_id = None
    if "target_role" not in st.session_state:
        st.session_state.target_role = "GenAI Engineer"
    if "full_analysis" not in st.session_state:
        st.session_state.full_analysis = None
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False


def main():
    init_session_state()

    # Sidebar Header & Navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        st.markdown("---")

        page = st.radio(
            "Select View:",
            [
                "🏠 Home & Dashboard",
                "📄 Resume Upload",
                "👤 Candidate Profile",
                "🎯 Career Match",
                "📊 Market Intelligence",
                "🧩 Skill Gap Analysis",
                "🗺️ Learning Roadmap",
                "💡 Recommended Projects",
                "🎯 Interview Preparation",
                "⚙️ System Status",
            ],
            index=0,
        )

        st.markdown("---")
        health_data = api_client.check_health()
        if health_data:
            st.markdown("🟢 **Backend Connected**")
            if health_data.get("demo_mode") or st.session_state.demo_mode:
                st.info("ℹ️ **DEMO MODE ACTIVE**")
        else:
            st.markdown("🔴 **Backend Offline**")
            st.caption("Start server: `uvicorn backend.main:app --port 8000`")

        if st.session_state.candidate_id:
            st.divider()
            st.caption(f"Active Candidate ID: #{st.session_state.candidate_id}")
            st.caption(f"Active Role: {st.session_state.target_role}")

    # View Routing
    if page == "🏠 Home & Dashboard":
        render_home_view(st.session_state.full_analysis, st.session_state.demo_mode)
    elif page == "📄 Resume Upload" or page == "👤 Candidate Profile":
        render_resume_view(st.session_state.full_analysis)
    elif page == "🎯 Career Match":
        render_career_view(st.session_state.full_analysis)
    elif page == "📊 Market Intelligence":
        render_market_view(st.session_state.full_analysis)
    elif page == "🧩 Skill Gap Analysis":
        render_skill_gap_view(st.session_state.full_analysis)
    elif page == "🗺️ Learning Roadmap":
        render_roadmap_view(st.session_state.full_analysis)
    elif page == "💡 Recommended Projects":
        render_projects_view(st.session_state.full_analysis)
    elif page == "🎯 Interview Preparation":
        render_interview_view(st.session_state.full_analysis)
    elif page == "⚙️ System Status":
        render_status_view()


if __name__ == "__main__":
    main()
