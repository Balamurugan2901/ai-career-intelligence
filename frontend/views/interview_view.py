import streamlit as st
from typing import Dict, Any, Optional


def render_interview_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders Interview Preparation & Question Generator page."""
    st.markdown('<div class="hero-title">Interview Preparation & Question Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Targeted interview questions across 8 categories with structural answer frameworks and evaluation points</div>', unsafe_allow_html=True)

    if not full_analysis or "interview_preparation" not in full_analysis:
        st.info("No interview prep loaded. Upload a resume or select a demo candidate to view interview questions.")
        return

    interview_data = full_analysis.get("interview_preparation", {})
    categories = interview_data.get("categories", [])
    total_q = interview_data.get("total_questions", 0)

    st.markdown(f"### Total Tailored Questions: <span style='color: #38BDF8;'>{total_q} Questions</span> across 8 Categories", unsafe_allow_html=True)

    sources = interview_data.get("sources", [])
    if sources:
        from frontend.styles import render_evidence_sources
        render_evidence_sources(sources, title="Evidence & Sources for Interview Preparation")

    st.divider()

    if not categories:
        st.write("No interview questions available.")
        return

    for cat in categories:
        cat_name = cat.get("category_name", "General Category")
        questions = cat.get("questions", [])

        with st.expander(f"📚 {cat_name} ({len(questions)} Questions)", expanded=(cat_name in ["AI/ML Questions", "GenAI Questions", "Technical Questions"])):
            for idx, q in enumerate(questions, 1):
                q_text = q.get("question", f"Question {idx}")
                difficulty = q.get("difficulty", "Mid-Level").upper()
                concepts = q.get("expected_concepts", [])
                eval_pts = q.get("evaluation_points", [])
                answer_struct = q.get("model_answer_structure", "")

                badge_class = "badge-low" if "JUNIOR" in difficulty else ("badge-medium" if "MID" in difficulty else "badge-high")

                st.markdown(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <h4 style="margin: 0; color: #F8FAFC; flex-grow: 1; font-weight: 600;">Q{idx}: {q_text}</h4>
                        <span class="badge {badge_class}" style="margin-left: 1rem;">{difficulty}</span>
                    </div>
                    
                    <div style="margin-top: 0.6rem;">
                        <b>Core Concepts Evaluated:</b>
                        {"".join([f'<span class="skill-pill">{c}</span>' for c in concepts])}
                    </div>

                    <div style="margin-top: 0.8rem;">
                        <b>Key Evaluation Points (What Interviewer Looks For):</b>
                        <ul style="margin-bottom: 0.4rem; color: #94A3B8;">
                            {"".join([f'<li>{pt}</li>' for pt in eval_pts])}
                        </ul>
                    </div>

                    <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #34D399; padding: 0.8rem; border-radius: 6px; margin-top: 0.8rem;">
                        <b style="color: #34D399;">💡 Recommended Answer Structural Framework:</b>
                        <p style="margin: 0.3rem 0 0 0; color: #E2E8F0; white-space: pre-wrap;">{answer_struct}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
