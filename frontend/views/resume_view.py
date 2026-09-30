import streamlit as st
from typing import Dict, Any, Optional
from frontend.services.api_client import api_client


def render_resume_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders Resume Upload & Structured Candidate Profile page."""
    st.markdown('<div class="hero-title">Candidate Resume & Profile Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Extract structured candidate profile, categorized skills, experience timeline, and strengths</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📄 Upload Resume", "👤 Structured Profile"])

    with tab1:
        st.markdown("### Upload Candidate Resume (PDF or DOCX)")
        uploaded_file = st.file_uploader(
            "Select resume file (Max 5MB)",
            type=["pdf", "docx"],
            help="Upload a PDF or Word document containing candidate work experience and skills."
        )

        if uploaded_file:
            # Client side validation
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 5.0:
                st.error(f"❌ File size exceeds 5MB limit ({file_size_mb:.2f} MB uploaded). Please upload a smaller file.")
            else:
                st.success(f"✅ Selected `{uploaded_file.name}` ({file_size_mb * 1024:.1f} KB)")
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    if st.button("⚡ Upload & Analyze Resume", type="primary", use_container_width=True):
                        try:
                            with st.spinner("Parsing resume and initiating 7-Agent Analysis Pipeline..."):
                                file_bytes = uploaded_file.getvalue()
                                res = api_client.upload_resume(file_bytes, uploaded_file.name)
                                candidate_id = res["candidate_id"]
                                st.session_state.candidate_id = candidate_id
                                
                                # Trigger end-to-end pipeline
                                analysis_data = api_client.start_pipeline_analysis(candidate_id=candidate_id)
                                analysis_id = analysis_data["analysis_id"]
                                st.session_state.analysis_id = analysis_id

                                # Fetch full results
                                full_data = api_client.get_full_analysis(candidate_id=candidate_id)
                                st.session_state.full_analysis = full_data
                                st.session_state.target_role = full_data.get("target_role", "GenAI Engineer")
                                
                                st.success("🎉 Full 7-Agent Pipeline Execution Completed Successfully!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Failed to process resume: {str(e)}")

    with tab2:
        if not full_analysis or "profile" not in full_analysis:
            st.info("No candidate profile loaded. Upload a resume above or load a sample candidate from the Home page.")
        else:
            profile = full_analysis.get("profile", {})
            st.markdown(f"## {profile.get('name', 'Candidate Profile')}")
            st.markdown(f"**Professional Summary:** {profile.get('professional_summary', 'No summary provided.')}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Years of Experience", f"{profile.get('years_of_experience', 0.0)} Years")
            with c2:
                st.metric("Education Level", profile.get("education_level") or "Bachelor's Degree")

            st.divider()

            # Categorized Skills Pills
            st.markdown("### 🛠️ Categorized Skills Matrix")
            skills_data = profile.get("skills", {})
            if isinstance(skills_data, dict):
                for category, skills in skills_data.items():
                    if skills:
                        cat_title = category.replace("_", " ").title()
                        pills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in skills])
                        st.markdown(f"**{cat_title}:**<br>{pills_html}", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

            st.divider()

            # Experience Timeline
            st.markdown("### 💼 Work Experience")
            work_items = profile.get("work_experience", [])
            if work_items:
                for work in work_items:
                    st.markdown(f"""
                    <div class="glass-card">
                        <h4 style="margin: 0; color: #38BDF8;">{work.get('role_title', 'Role')} @ {work.get('company', 'Company')}</h4>
                        <p style="color: #94A3B8; font-size: 0.85rem;">{work.get('duration', '')}</p>
                        <p>{work.get('description', '')}</p>
                        <div><b>Key Achievements:</b> {', '.join(work.get('key_achievements', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No work experience listed.")

            st.divider()

            # Strengths & Missing Information
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 💪 Identified Strengths")
                strengths = profile.get("strengths", {})
                if isinstance(strengths, dict):
                    for key, items in strengths.items():
                        if items:
                            st.markdown(f"**{key.replace('_', ' ').title()}:**")
                            for item in items:
                                st.markdown(f"- {item}")
                elif isinstance(strengths, list):
                    for item in strengths:
                        st.markdown(f"- {item}")

            with col2:
                st.markdown("### ⚠️ Missing / Unclear Information")
                missing = profile.get("missing_information", {})
                if isinstance(missing, dict):
                    for key, items in missing.items():
                        if items:
                            st.markdown(f"**{key.replace('_', ' ').title()}:**")
                            for item in items:
                                st.markdown(f"- {item}")
                elif isinstance(missing, list):
                    for item in missing:
                        st.markdown(f"- {item}")
