"""Global CSS injection for NEXUS Streamlit apps."""

from __future__ import annotations

from theme.tokens import (
    BORDER,
    CARD_BG,
    GREEN,
    GREEN_BG,
    ORANGE,
    ORANGE_LIGHT,
    PAGE_BG,
    RED,
    RED_BG,
    SIDEBAR_BG,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


def inject_styles() -> None:
    from theme.html_utils import render_html

    render_html(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        #MainMenu, footer {{
            visibility: hidden;
            height: 0;
        }}

        header[data-testid="stHeader"] {{
            background: transparent;
        }}

        button[data-testid="stSidebarCollapsedControl"],
        button[data-testid="baseButton-headerNoPadding"] {{
            visibility: visible !important;
        }}

        .stApp {{
            background-color: {PAGE_BG};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
            border-right: none;
            min-width: 240px !important;
            max-width: 240px !important;
            display: block !important;
            visibility: visible !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
            width: 100%;
            justify-content: flex-start;
            background: transparent;
            color: #D1D5DB;
            border: none;
            font-weight: 500;
            font-size: 0.9rem;
            padding: 0.55rem 0.85rem;
            margin-bottom: 0.15rem;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
            background: #333333;
            color: #FFFFFF;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {{
            background: {ORANGE} !important;
            color: #FFFFFF !important;
        }}

        section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {{
            background: {ORANGE} !important;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: {SIDEBAR_BG};
            padding-top: 0;
        }}

        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {{
            color: #FFFFFF;
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: #333;
            margin: 1rem 0;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }}

        .nexus-logo {{
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-bottom: 1.75rem;
            padding-top: 0.5rem;
        }}

        .nexus-logo .mark {{ color: {ORANGE}; }}

        .nav-item {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.55rem 0.85rem;
            border-radius: 8px;
            color: #D1D5DB;
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.15rem;
            cursor: pointer;
        }}

        .nav-item.active {{
            background: {ORANGE};
            color: #FFFFFF;
        }}

        .nav-section {{
            color: #9CA3AF;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin: 1.25rem 0 0.5rem 0.85rem;
        }}

        .account-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.75rem 0.85rem;
            border-top: 1px solid #333;
            margin-top: 2rem;
            color: #FFFFFF;
            font-size: 0.9rem;
        }}

        .page-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }}

        .page-header h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin: 0;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .icon-btn {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: {CARD_BG};
            border: 1px solid {BORDER};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }}

        .profile-chip {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 999px;
            padding: 0.25rem 0.5rem 0.25rem 0.25rem;
        }}

        .profile-avatar {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FCD34D, {ORANGE});
        }}

        .card {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
        }}

        .section-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            margin-bottom: 1rem;
        }}

        .section-header h2 {{
            margin: 0;
            font-size: 1.15rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
        }}

        .section-header .subtitle {{
            color: {TEXT_MUTED};
            font-size: 0.78rem;
            margin-top: 0.15rem;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .metric-card {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.1rem 1.25rem;
        }}

        .metric-label {{
            color: {ORANGE};
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }}

        .metric-value {{
            font-size: 1.65rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-bottom: 0.65rem;
        }}

        .delta-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
        }}

        .delta-badge.positive {{ background: {GREEN_BG}; color: {GREEN}; }}
        .delta-badge.negative {{ background: {RED_BG}; color: {RED}; }}

        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 600;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}

        .data-table th {{
            text-align: left;
            color: {TEXT_MUTED};
            font-weight: 500;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid {BORDER};
        }}

        .data-table td {{
            padding: 0.85rem 1rem;
            border-bottom: 1px solid {BORDER};
            color: {TEXT_PRIMARY};
        }}

        .data-table tr:last-child td {{ border-bottom: none; }}

        .warning-banner {{
            background: {ORANGE_LIGHT};
            border: 1px solid #FDEAD7;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            color: {TEXT_PRIMARY};
            margin-bottom: 1rem;
        }}

        .empty-state {{
            text-align: center;
            padding: 3rem 2rem;
            color: {TEXT_MUTED};
        }}

        div[data-testid="stPlotlyChart"] {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 0.75rem;
        }}

        .hero-card {{
            background: linear-gradient(135deg, {ORANGE_LIGHT} 0%, #FFFFFF 55%, #FFFFFF 100%);
            border: 1px solid #FDEAD7;
            border-radius: 12px;
            padding: 2rem 2rem 2rem 2.25rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2rem;
            margin-bottom: 1rem;
            overflow: hidden;
            min-height: 210px;
        }}

        .hero-card h2 {{
            font-size: 1.65rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin: 0 0 1rem 0;
        }}

        .hero-list {{ list-style: none; padding: 0; margin: 0; }}
        .hero-list li {{
            display: flex; align-items: center; gap: 0.5rem;
            color: {TEXT_MUTED}; font-size: 0.95rem; margin-bottom: 0.45rem;
        }}
        .hero-list li::before {{ content: "→"; color: {ORANGE}; font-weight: 700; }}

        .hero-devices {{ position: relative; width: 280px; height: 170px; flex-shrink: 0; }}
        .device-laptop {{
            position: absolute; right: 0; top: 10px; width: 210px; height: 130px;
            background: #FFF; border-radius: 8px; border: 2px solid #E5E7EB;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08); padding: 8px;
        }}
        .device-phone {{
            position: absolute; left: 0; bottom: 0; width: 72px; height: 120px;
            background: #FFF; border-radius: 12px; border: 2px solid #E5E7EB;
            box-shadow: 0 6px 18px rgba(0,0,0,0.1); padding: 6px;
        }}
        .device-screen {{
            width: 100%; height: 100%;
            background: linear-gradient(180deg, {ORANGE_LIGHT}, #FFFFFF);
            border-radius: 4px;
        }}

        .feature-card {{ display: flex; gap: 1rem; align-items: flex-start; }}
        .feature-icon {{
            width: 40px; height: 40px; border-radius: 8px; background: {PAGE_BG};
            border: 1px solid {BORDER}; display: flex; align-items: center;
            justify-content: center; font-size: 1.1rem; flex-shrink: 0;
        }}
        .feature-card h3 {{ margin: 0 0 0.35rem 0; font-size: 1rem; font-weight: 600; }}
        .feature-card p {{ margin: 0; color: {TEXT_MUTED}; font-size: 0.88rem; line-height: 1.5; }}

        .toolbar {{ display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }}
        .select-pill, .btn-outline {{
            background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 8px;
            padding: 0.4rem 0.75rem; font-size: 0.82rem; color: {TEXT_PRIMARY};
        }}
        .btn-outline {{ display: inline-flex; align-items: center; gap: 0.35rem; }}

        .partners-table {{
            width: 100%; border-collapse: collapse; font-size: 0.88rem;
        }}
        .partners-table th {{
            text-align: left; color: {TEXT_MUTED}; font-weight: 500;
            padding: 0.75rem 1rem; border-bottom: 1px solid {BORDER};
        }}
        .partners-table td {{
            padding: 0.85rem 1rem; border-bottom: 1px solid {BORDER}; color: {TEXT_PRIMARY};
        }}
        .partners-table tr:last-child td {{ border-bottom: none; }}

        @media (max-width: 1100px) {{
            .metric-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .hero-card {{ flex-direction: column; align-items: flex-start; }}
        }}
        </style>
        """
    )
