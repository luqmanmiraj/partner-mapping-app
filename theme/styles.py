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
    from theme.sidenav import inject_sidenav_styles
    from theme.top_header import inject_top_header_styles

    inject_sidenav_styles()
    inject_top_header_styles()
    from theme.page_content import inject_page_content_styles
    from widgets.overview_section import inject_overview_section_styles

    inject_page_content_styles()
    inject_overview_section_styles()

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

        /* Expand control when sidebar is collapsed (main canvas, not in-sidebar header) */
        button[data-testid="stSidebarCollapsedControl"] {{
            visibility: visible !important;
        }}

        /* Remove Streamlit default sidebar header (logo spacer + collapse button) */
        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
        section[data-testid="stSidebar"] [data-testid="stLogoSpacer"],
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {{
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            overflow: hidden !important;
            visibility: hidden !important;
        }}

        .stApp {{
            background-color: {PAGE_BG};
        }}

        section[data-testid="stSidebar"] {{
            background-color: #111111 !important;
            border-right: none;
            min-width: 280px !important;
            max-width: 280px !important;
            display: block !important;
            visibility: visible !important;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: #111111;
            padding-top: 0;
        }}

        section[data-testid="stSidebar"]
        div[data-testid="stVerticalBlockBorderWrapper"]:not([class*="st-key-navbtn_"]):not(
            [class*="st-key-sidenav_"]
        )
        div[data-testid="stButton"]
        > button {{
            width: 100%;
            justify-content: flex-start;
            background: #1a1a1a;
            color: #e5e5e5;
            border: 1px solid #333333;
            font-weight: 500;
            font-size: 0.85rem;
            padding: 0.45rem 0.75rem;
            margin-bottom: 0.35rem;
        }}

        section[data-testid="stSidebar"]
        div[data-testid="stVerticalBlockBorderWrapper"]:not([class*="st-key-navbtn_"]):not(
            [class*="st-key-sidenav_"]
        )
        div[data-testid="stButton"]
        > button:hover {{
            background: #262626;
            color: #ffffff;
            border-color: #444444;
        }}

        section[data-testid="stSidebar"] .stCaption,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stSelectbox label {{
            color: #b0b0b0 !important;
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: #333333;
            margin: 1rem 0;
        }}

        .block-container {{
            padding-top: 0;
            padding-left: 0;
            padding-right: 0;
            max-width: 100%;
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
        }}
        </style>
        """
    )
