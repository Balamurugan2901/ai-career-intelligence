import streamlit as st
from frontend.services.api_client import api_client


def render_status_view():
    """Renders System Status & Infrastructure Monitoring page."""
    st.markdown('<div class="hero-title">System Infrastructure & API Health</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Real-time status of FastAPI backend server, database schemas, and demo mode settings</div>', unsafe_allow_html=True)

    health_data = api_client.check_health()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #38BDF8; margin-top: 0;">Backend API Service</h3>
        """, unsafe_allow_html=True)

        if health_data:
            st.success("🟢 FastAPI Backend Server is ONLINE")
            st.json(health_data)
        else:
            st.error("🔴 FastAPI Backend Server is OFFLINE")
            st.warning("Start the server locally using:\n`uvicorn backend.main:app --port 8000`")

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #818CF8; margin-top: 0;">System Configuration</h3>
        """, unsafe_allow_html=True)

        st.write(f"**Backend URL:** `{api_client.base_url}`")
        st.write(f"**Interactive OpenAPI Docs:** [http://127.0.0.1:8000/docs]({api_client.base_url}/docs)")
        st.write(f"**ReDoc Endpoint:** [http://127.0.0.1:8000/redoc]({api_client.base_url}/redoc)")

        st.divider()
        st.markdown("### Demo Mode Control")
        st.write("Demo mode allows presentation without an active Google Gemini API key.")

        is_demo = st.session_state.get("demo_mode", False)
        if st.checkbox("Force UI Demo Mode", value=is_demo):
            st.session_state.demo_mode = True
            st.info("UI running in Forced Demo Mode.")
        else:
            st.session_state.demo_mode = False

        st.markdown("</div>", unsafe_allow_html=True)
