"""NEXUS Partner Dashboard — Streamlit prototype matching the maquette design."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from dashboard_data import DashboardData, load_demo_data, load_from_snowflake
from snowflake_client import SnowflakeConnectionError, SnowflakeMfaRequired, connect

# ── Design tokens ─────────────────────────────────────────────────────────────
ORANGE = "#F58220"
ORANGE_LIGHT = "#FFF4EB"
SIDEBAR_BG = "#1C1C1E"
PAGE_BG = "#F4F4F5"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#1A1A1A"
TEXT_MUTED = "#6B7280"
GREEN = "#059669"
GREEN_BG = "#ECFDF5"
RED = "#DC2626"
RED_BG = "#FEF2F2"
BORDER = "#E5E7EB"


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}

        #MainMenu, footer, header[data-testid="stHeader"] {{
            visibility: hidden;
            height: 0;
        }}

        .stApp {{
            background-color: {PAGE_BG};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG};
            border-right: none;
            min-width: 240px !important;
            max-width: 240px !important;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: {SIDEBAR_BG};
            padding-top: 0;
        }}

        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span {{
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

        div[data-testid="stVerticalBlock"] > div:has(> div.element-container) {{
            gap: 0.4rem;
        }}

        .nexus-logo {{
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-bottom: 1.75rem;
            padding-top: 0.5rem;
        }}

        .nexus-logo .mark {{
            color: {ORANGE};
        }}

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
            color: {TEXT_PRIMARY};
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
            line-height: 1.25;
        }}

        .hero-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .hero-list li {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: {TEXT_MUTED};
            font-size: 0.95rem;
            margin-bottom: 0.45rem;
        }}

        .hero-list li::before {{
            content: "→";
            color: {ORANGE};
            font-weight: 700;
        }}

        .hero-devices {{
            position: relative;
            width: 280px;
            height: 170px;
            flex-shrink: 0;
        }}

        .device-laptop {{
            position: absolute;
            right: 0;
            top: 10px;
            width: 210px;
            height: 130px;
            background: #FFFFFF;
            border-radius: 8px;
            border: 2px solid #E5E7EB;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            padding: 8px;
        }}

        .device-laptop::after {{
            content: "";
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 80%;
            height: 6px;
            background: #D1D5DB;
            border-radius: 0 0 4px 4px;
        }}

        .device-phone {{
            position: absolute;
            left: 0;
            bottom: 0;
            width: 72px;
            height: 120px;
            background: #FFFFFF;
            border-radius: 12px;
            border: 2px solid #E5E7EB;
            box-shadow: 0 6px 18px rgba(0,0,0,0.1);
            padding: 6px;
        }}

        .device-screen {{
            width: 100%;
            height: 100%;
            background: linear-gradient(180deg, {ORANGE_LIGHT}, #FFFFFF);
            border-radius: 4px;
        }}

        .device-phone .device-screen {{
            border-radius: 8px;
        }}

        .feature-card {{
            display: flex;
            gap: 1rem;
            align-items: flex-start;
            margin-bottom: 1.5rem;
        }}

        .feature-icon {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            background: {PAGE_BG};
            border: 1px solid {BORDER};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.1rem;
            flex-shrink: 0;
        }}

        .feature-card h3 {{
            margin: 0 0 0.35rem 0;
            font-size: 1rem;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        }}

        .feature-card p {{
            margin: 0;
            color: {TEXT_MUTED};
            font-size: 0.88rem;
            line-height: 1.5;
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

        .toolbar {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .select-pill, .btn-outline {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 0.4rem 0.75rem;
            font-size: 0.82rem;
            color: {TEXT_PRIMARY};
            white-space: nowrap;
        }}

        .btn-outline {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            cursor: default;
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

        .delta-badge.positive {{
            background: {GREEN_BG};
            color: {GREEN};
        }}

        .delta-badge.negative {{
            background: {RED_BG};
            color: {RED};
        }}

        .chart-card {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1rem 1rem 0.5rem 1rem;
            height: 100%;
        }}

        .chart-card h3 {{
            margin: 0 0 0.75rem 0;
            font-size: 0.95rem;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        }}

        div[data-testid="stPlotlyChart"] {{
            background: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 0.75rem 0.75rem 0.25rem 0.75rem;
        }}

        .partners-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}

        .partners-table th {{
            text-align: left;
            color: {TEXT_MUTED};
            font-weight: 500;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid {BORDER};
        }}

        .partners-table td {{
            padding: 0.85rem 1rem;
            border-bottom: 1px solid {BORDER};
            color: {TEXT_PRIMARY};
        }}

        .partners-table tr:last-child td {{
            border-bottom: none;
        }}

        @media (max-width: 1100px) {{
            .metric-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .hero-card {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .hero-devices {{
                align-self: center;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_nav() -> None:
    st.markdown(
        """
        <div class="nexus-logo">
            <span class="mark">N!</span> NEXUS
        </div>
        <div class="nav-item active">▦ Dashboard</div>
        <div class="nav-item">👥 Member Directory</div>
        <div class="nav-item">🏢 My Company</div>
        <div class="nav-section">Nexus Automotive</div>
        <div class="nav-item">About</div>
        <div class="nav-item">Services</div>
        <div class="nav-item">News &amp; Insights</div>
        <div class="nav-item">Help &amp; Support Center</div>
        <div class="account-row">
            <span>👤 My account</span>
            <span>⌃</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_controls() -> tuple[bool, str]:
    st.divider()
    use_snowflake = st.toggle("Use Snowflake data", value=st.session_state.get("use_snowflake", True))
    passcode = st.text_input(
        "TOTP passcode (if MFA enabled)",
        value=st.session_state.get("passcode", ""),
        type="password",
        help="Uses destination credentials from scripts/snowflake_migrate/.env.migrate",
    )
    if st.button("Refresh data"):
        fetch_dashboard_data.clear()
    st.session_state.use_snowflake = use_snowflake
    st.session_state.passcode = passcode
    return use_snowflake, passcode


def render_sidebar_status(data: DashboardData) -> None:
    if data.source == "snowflake":
        st.success("Connected to PM_PROD.REF")
    else:
        st.warning("Using demo data")
    if data.error:
        st.caption(data.error)


@st.cache_data(ttl=300, show_spinner="Loading from Snowflake…")
def fetch_dashboard_data(passcode: str) -> DashboardData:
    conn = connect(passcode=passcode)
    try:
        return load_from_snowflake(conn)
    finally:
        conn.close()


def resolve_dashboard_data(use_snowflake: bool, passcode: str) -> DashboardData:
    if not use_snowflake:
        return load_demo_data()
    try:
        return fetch_dashboard_data(passcode)
    except SnowflakeMfaRequired:
        demo = load_demo_data()
        demo.error = "Snowflake MFA required — enter your TOTP passcode in the sidebar."
        return demo
    except SnowflakeConnectionError as exc:
        demo = load_demo_data()
        demo.error = str(exc)
        return demo


def render_page_header() -> None:
    st.markdown(
        """
        <div class="page-header">
            <h1>Welcome Elina,</h1>
            <div class="header-actions">
                <div class="icon-btn">🔔</div>
                <div class="profile-chip">
                    <div class="profile-avatar"></div>
                    <span>▾</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <div>
                <h2>Welcome to your centralized hub.</h2>
                <ul class="hero-list">
                    <li>Drive your performance</li>
                    <li>Access exclusive deals</li>
                    <li>And stay connected with the global Nexus ecosystem</li>
                </ul>
            </div>
            <div class="hero-devices">
                <div class="device-phone"><div class="device-screen"></div></div>
                <div class="device-laptop"><div class="device-screen"></div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upcoming_features() -> None:
    st.markdown(
        """
        <div class="card feature-card">
            <div class="feature-icon">▦</div>
            <div>
                <h3>Upcoming features</h3>
                <p>
                    Soon you will be able to discover supplier books, key performances,
                    and data analysis — all in one place to help you make smarter decisions.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_toolbar(title: str, last_updated: str, show_controls: bool = False) -> None:
    controls = ""
    if show_controls:
        controls = """
            <div class="toolbar">
                <span class="select-pill">Date ▾</span>
                <span class="select-pill">Lorem ipsum ▾</span>
                <span class="btn-outline">⬆ Import</span>
                <span class="btn-outline">⬇ Export</span>
            </div>
        """
    st.markdown(
        f"""
        <div class="section-header">
            <div>
                <h2>{title}</h2>
                <div class="subtitle">Last updated: {last_updated}</div>
            </div>
            {controls}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(cards: list[dict]) -> None:
    cards_html = ""
    for card in cards:
        badge_class = "positive" if card["positive"] else "negative"
        arrow = "↗" if card["positive"] else "↘"
        cards_html += f"""
        <div class="metric-card">
            <div class="metric-label">{card["label"]}</div>
            <div class="metric-value">{card["value"]}</div>
            <span class="delta-badge {badge_class}">{arrow} {card["delta"]}</span>
        </div>
        """
    st.markdown(f'<div class="metric-grid">{cards_html}</div>', unsafe_allow_html=True)


def _series(df: pd.DataFrame, *column_candidates: str) -> pd.Series:
    for col in column_candidates:
        if col in df.columns:
            return df[col]
        upper = col.upper()
        if upper in df.columns:
            return df[upper]
    raise KeyError(f"None of {column_candidates} found in {list(df.columns)}")


def build_area_chart(df: pd.DataFrame, *, title: str) -> go.Figure:
    x = _series(df, "region", "REGION")
    y = _series(df, "member_count", "MEMBER_COUNT")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=ORANGE, width=2, dash="dot"),
            fill="tozeroy",
            fillcolor="rgba(245, 130, 32, 0.18)",
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=TEXT_PRIMARY)),
        margin=dict(l=10, r=10, t=40, b=30),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color=TEXT_MUTED), linecolor=BORDER),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=11, color=TEXT_MUTED), linecolor=BORDER),
        showlegend=False,
        hovermode="x unified",
    )
    return fig


def build_bar_chart(df: pd.DataFrame, *, title: str) -> go.Figure:
    labels = _series(df, "country", "COUNTRY").astype(str)
    values = _series(df, "member_count", "MEMBER_COUNT").astype(float)
    fig = go.Figure(
        go.Bar(
            y=labels,
            x=values,
            orientation="h",
            marker=dict(
                color=values,
                colorscale=[[0, "#FDEAD7"], [1, ORANGE]],
                line=dict(width=0),
            ),
            text=[str(int(v)) for v in values],
            textposition="outside",
            textfont=dict(size=11, color=TEXT_PRIMARY),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=TEXT_PRIMARY)),
        margin=dict(l=10, r=40, t=40, b=10),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color=TEXT_PRIMARY), autorange="reversed"),
        showlegend=False,
    )
    return fig


def render_sales_charts(data: DashboardData) -> None:
    left_title = "Members by Region" if data.source == "snowflake" else "Sales by Country"
    right_title = "Members by Country" if data.source == "snowflake" else "Sales by Product Group"
    col_left, col_right = st.columns(2, gap="medium")
    with col_left:
        if not data.region_chart.empty:
            st.plotly_chart(
                build_area_chart(data.region_chart, title=left_title),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.info("No regional member data available.")
    with col_right:
        if not data.country_chart.empty:
            st.plotly_chart(
                build_bar_chart(data.country_chart, title=right_title),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.info("No country member data available.")


def render_partners_table(partners: pd.DataFrame) -> None:
    if partners.empty:
        st.info("No partner rows available.")
        return
    rows = ""
    for _, row in partners.iterrows():
        member = row.get("Member", row.get("MEMBER", ""))
        country = row.get("Country", row.get("COUNTRY", ""))
        volume = row.get("Volume", row.get("VOLUME", ""))
        growth = row.get("Growth", row.get("GROWTH", ""))
        positive = bool(row.get("positive", row.get("POSITIVE", True)))
        badge_class = "positive" if positive else "negative"
        arrow = "↗" if positive else "↘"
        rows += f"""
        <tr>
            <td>{member}</td>
            <td>{country}</td>
            <td>{volume}</td>
            <td><span class="delta-badge {badge_class}">{arrow} {growth}</span></td>
        </tr>
        """
    st.markdown(
        f"""
        <div class="card" style="padding: 0; overflow: hidden;">
            <table class="partners-table">
                <thead>
                    <tr>
                        <th>Member</th>
                        <th>Country</th>
                        <th>Volume</th>
                        <th>Growth</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="NEXUS Dashboard",
        page_icon="▦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()

    with st.sidebar:
        render_sidebar_nav()
        use_snowflake, passcode = render_sidebar_controls()

    data = resolve_dashboard_data(use_snowflake, passcode)

    with st.sidebar:
        render_sidebar_status(data)

    render_page_header()

    render_hero()
    render_upcoming_features()

    from content_policies.hub_dashboard import HubDashboardPolicy
    from widgets.overview_section import render_overview_section

    render_overview_section(HubDashboardPolicy(), data.last_updated, data.overview_cards)

    render_section_toolbar("Sales", data.last_updated)
    render_sales_charts(data)

    render_section_toolbar("Top Performing Partners", data.last_updated)
    render_partners_table(data.partners)


if __name__ == "__main__":
    main()
