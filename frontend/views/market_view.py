import streamlit as st
from typing import Dict, Any, Optional


def render_market_view(full_analysis: Optional[Dict[str, Any]]):
    """Renders Market Intelligence Analysis page."""
    st.markdown('<div class="hero-title">Market Intelligence & Role Benchmarks</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Industry demand metrics, required tooling, and emerging skill benchmarks</div>', unsafe_allow_html=True)

    if not full_analysis or "market_intelligence" not in full_analysis:
        st.info("No market intelligence data loaded. Please run analysis on a candidate resume first.")
        return

    market_data = full_analysis.get("market_intelligence", [])

    for role_item in market_data:
        role_name = role_item.get("role_name", "Target Role")
        demand_level = role_item.get("demand_level", "MEDIUM DEMAND").upper()
        top_skills = role_item.get("top_required_skills", [])
        emerging_skills = role_item.get("emerging_skills", [])
        salary_range = role_item.get("avg_salary_range", "N/A")
        updated_at = role_item.get("updated_at", "Recent")
        source_info = role_item.get("source", "Market insight based on configured reference data")

        # Select demand badge CSS class
        badge_class = "badge-high" if "HIGH" in demand_level else ("badge-medium" if "MEDIUM" in demand_level else "badge-low")

        with st.container():
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0; color: #38BDF8;">{role_name}</h3>
                    <span class="badge {badge_class}">{demand_level}</span>
                </div>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.4rem;">
                    ℹ️ <b>Data Source:</b> {source_info} | <b>Updated:</b> {updated_at}
                </p>
                <div style="margin-top: 0.8rem;">
                    <b>Average Compensation Benchmark:</b> <span style="color: #34D399; font-weight: 700;">{salary_range}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Top Required Core Industry Skills:**")
                if top_skills:
                    pills = "".join([f'<span class="skill-pill">{s}</span>' for s in top_skills])
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.write("N/A")

            with col2:
                st.markdown("**Emerging Tools & Frameworks:**")
                if emerging_skills:
                    pills = "".join([f'<span class="skill-pill" style="background: rgba(129, 140, 248, 0.15); border-color: #818CF8; color: #C084FC;">{s}</span>' for s in emerging_skills])
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.write("N/A")

            # Evidence & Provenance Inspector
            sources = role_item.get("sources", [])
            if sources:
                from frontend.styles import render_evidence_sources
                render_evidence_sources(sources, title=f"Evidence & Sources for {role_name} Market Data")

            st.divider()

