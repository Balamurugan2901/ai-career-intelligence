import streamlit as st

def apply_custom_styles():
    """Injects custom CSS styling for high-grade dark mode glassmorphism dashboard UI."""
    st.markdown("""
        <style>
        /* Main Application Container & Typography */
        .stApp {
            background-color: #0F172A;
            color: #F8FAFC;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* Top Hero Header */
        .hero-title {
            font-size: 2.3rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #94A3B8;
            margin-bottom: 1.8rem;
            font-weight: 400;
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
        }

        .glass-card:hover {
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 6px 25px -2px rgba(56, 189, 248, 0.15);
        }

        /* Metric Cards */
        .metric-box {
            background: linear-gradient(145deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }

        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #38BDF8;
            margin: 0.3rem 0;
        }

        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .metric-delta {
            font-size: 0.85rem;
            color: #34D399;
            font-weight: 500;
        }

        /* Badges & Pills */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-right: 0.4rem;
            margin-bottom: 0.3rem;
        }

        .badge-high {
            background: rgba(239, 68, 68, 0.2);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        .badge-medium {
            background: rgba(245, 158, 11, 0.2);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }

        .badge-low {
            background: rgba(59, 130, 246, 0.2);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.4);
        }

        .badge-fit {
            background: rgba(16, 185, 129, 0.2);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .skill-pill {
            display: inline-block;
            background: #1E293B;
            border: 1px solid #475569;
            color: #E2E8F0;
            padding: 0.3rem 0.7rem;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 500;
            margin: 0.25rem;
        }

        .skill-pill-strength {
            background: rgba(16, 185, 129, 0.15);
            border-color: rgba(16, 185, 129, 0.4);
            color: #6EE7B7;
        }

        .skill-pill-gap {
            background: rgba(239, 68, 68, 0.15);
            border-color: rgba(239, 68, 68, 0.4);
            color: #FCA5A5;
        }

        /* Timeline & Phase Cards */
        .phase-header {
            font-size: 1.1rem;
            font-weight: 700;
            color: #38BDF8;
            border-bottom: 2px solid #334155;
            padding-bottom: 0.4rem;
            margin-bottom: 0.8rem;
        }

        /* Pipeline Step Indicator */
        .step-active {
            color: #38BDF8;
            font-weight: 700;
        }

        .step-complete {
            color: #34D399;
        }

        .step-pending {
            color: #64748B;
        }
        </style>
    """, unsafe_allow_html=True)
