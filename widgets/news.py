"""News & Insights Widget — matches nexus-news.html prototype 1-to-1.

Architecture:
    CSS prefix: ``nxi`` (NEXUS Insights)

    Layout:
        1. CSS injected globally via st.markdown
        2. Top bar  — st.columns for title + "Request publication" button
        3. Nav tabs — styled st.buttons inside st.container(key="nxi_nav_tabs_row")
        4. Filter   — styled st.selectbox + clear button
        5. Two-col  — st.columns([3, 1]) guaranteed by Streamlit
              Left : hero + articles grid + pagination  → pure HTML
              Right: sidebar selects (Streamlit) + entrants list (HTML)

    No FontAwesome — all icons are inline SVG data-URIs.
"""

from __future__ import annotations

import html as html_lib

import streamlit as st

from data.news_fixtures import NEW_ENTRANTS, NEWS_ARTICLES

# ---------------------------------------------------------------------------
# SVG icon data-URIs
# ---------------------------------------------------------------------------
_ICO_PEN = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' stroke='%23ffffff' stroke-width='2' stroke-linecap='round' "
    "stroke-linejoin='round' viewBox='0 0 24 24'%3e"
    "%3cpath d='M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7'/%3e"
    "%3cpath d='M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z'/%3e"
    "%3c/svg%3e"
)

_ICO_USERS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' stroke='%23f39c12' stroke-width='2' stroke-linecap='round' "
    "stroke-linejoin='round' viewBox='0 0 24 24'%3e"
    "%3cpath d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'/%3e"
    "%3ccircle cx='9' cy='7' r='4'/%3e"
    "%3cpath d='M23 21v-2a4 4 0 0 0-3-3.87'/%3e"
    "%3cpath d='M16 3.13a4 4 0 0 1 0 7.75'/%3e"
    "%3c/svg%3e"
)

_ICO_MAP_PIN = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' stroke='%23666666' stroke-width='2' stroke-linecap='round' "
    "stroke-linejoin='round' viewBox='0 0 24 24'%3e"
    "%3cpath d='M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z'/%3e"
    "%3ccircle cx='12' cy='10' r='3'/%3e"
    "%3c/svg%3e"
)

_ICO_CHEV_L = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' stroke='%23555555' stroke-width='2.5' stroke-linecap='round' "
    "stroke-linejoin='round' viewBox='0 0 24 24'%3e"
    "%3cpolyline points='15 18 9 12 15 6'/%3e"
    "%3c/svg%3e"
)

_ICO_CHEV_R = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' stroke='%23555555' stroke-width='2.5' stroke-linecap='round' "
    "stroke-linejoin='round' viewBox='0 0 24 24'%3e"
    "%3cpolyline points='9 18 15 12 9 6'/%3e"
    "%3c/svg%3e"
)

_ICO_DROP = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "fill='none' stroke='%23555' stroke-width='2.5' viewBox='0 0 24 24'%3e"
    "%3cpolyline points='6 9 12 15 18 9'/%3e%3c/svg%3e"
)


# ---------------------------------------------------------------------------
# CSS — all styles in one injection
# ---------------------------------------------------------------------------
def _page_css() -> str:
    return f"""
<style>
/* ================================================================
   NXI — NEXUS Insights (prefix: nxi)
   ================================================================ */

/* Page wrapper background */
.st-key-nxi_page_wrap {{
    background-color: #eeeeee !important;
    padding: 24px !important;
    box-sizing: border-box !important;
    border-radius: 0 !important;
    border: none !important;
    box-shadow: none !important;
}}

/* ---- Top bar ---- */
.nxi-h1 {{
    font-size: 1.45rem;
    font-weight: 700;
    color: #000000;
    margin: 0;
    line-height: 1.3;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding-top: 4px;
}}

/* "Request publication" button */
.st-key-nxi_pub_btn button {{
    background-color: #141619 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 10px 16px !important;
    min-height: 0 !important;
    box-shadow: none !important;
    width: 100% !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}}

.st-key-nxi_pub_btn button:hover {{
    background-color: #2c3035 !important;
}}

.st-key-nxi_pub_btn button p {{
    margin: 0 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}}

/* ---- Nav Tabs row ---- */
.st-key-nxi_nav_tabs_row {{
    border-bottom: 1px solid #cccccc !important;
    padding-bottom: 0 !important;
    margin-bottom: 0 !important;
}}

/* Remove horizontal block gaps inside tab row */
.st-key-nxi_nav_tabs_row [data-testid="stHorizontalBlock"] {{
    gap: 0 !important;
    align-items: flex-end !important;
}}

/* Tab button wrappers */
.st-key-nxi_nav_tabs_row [data-testid="stColumn"] {{
    flex: 0 0 auto !important;
    width: auto !important;
    padding: 0 !important;
}}

/* All tab buttons base style */
.st-key-nxi_nav_tabs_row [data-testid="stButton"] button {{
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    border-bottom: 3px solid transparent !important;
    padding: 0 16px 12px 0 !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: #777777 !important;
    box-shadow: none !important;
    min-height: 0 !important;
    height: auto !important;
    white-space: nowrap !important;
    cursor: pointer !important;
    margin-bottom: -1px !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
}}

.st-key-nxi_nav_tabs_row [data-testid="stButton"] button:hover {{
    color: #000000 !important;
}}

/* Active tab = primary type */
.st-key-nxi_nav_tabs_row [data-testid="stButton"] button[data-testid="stBaseButton-primary"],
.st-key-nxi_nav_tabs_row [data-testid="stButton"] button[kind="primary"] {{
    color: #000000 !important;
    border-bottom-color: #f39c12 !important;
}}

.st-key-nxi_nav_tabs_row [data-testid="stButton"] button p {{
    margin: 0 !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    color: inherit !important;
}}

/* ---- Filter row ---- */
.st-key-nxi_filter_row [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
    gap: 12px !important;
    flex-wrap: nowrap !important;
    margin-top: 8px !important;
    margin-bottom: 8px !important;
}}

.st-key-nxi_filter_row [data-testid="stColumn"]:first-child {{
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 180px !important;
    max-width: 200px !important;
    padding: 0 !important;
}}

.st-key-nxi_filter_row [data-testid="stColumn"]:nth-child(2) {{
    flex: 0 0 auto !important;
    width: auto !important;
    padding: 0 !important;
}}

.st-key-nxi_filter_row [data-testid="stSelectbox"] label {{
    display: none !important;
}}

.st-key-nxi_filter_row [data-testid="stSelectbox"] [data-testid="stSelectboxRootElement"] {{
    border: 1px solid #cccccc !important;
    border-radius: 4px !important;
    background-color: #ffffff !important;
    height: 36px !important;
    box-shadow: none !important;
    min-height: 0 !important;
}}

.st-key-nxi_filter_row [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    padding: 0 12px !important;
    font-size: 0.84rem !important;
    color: #333333 !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
}}

/* Clear filters button */
.st-key-nxi_filter_row [data-testid="stButton"] button {{
    background: transparent !important;
    border: none !important;
    color: #000000 !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    padding: 4px 0 !important;
    min-height: 0 !important;
    height: auto !important;
    box-shadow: none !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    white-space: nowrap !important;
}}

.st-key-nxi_filter_row [data-testid="stButton"] button p {{
    margin: 0 !important;
    color: #000000 !important;
    font-weight: 700 !important;
}}

/* ---- Hero Banner ---- */
.nxi-hero-banner {{
    position: relative;
    width: 100%;
    height: 300px;
    border-radius: 4px;
    overflow: hidden;
    background-color: #141619;
    display: block;
}}

.nxi-hero-img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.35;
    display: block;
    position: absolute;
    top: 0;
    left: 0;
}}

.nxi-hero-overlay {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    padding: 32px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    color: #ffffff;
    box-sizing: border-box;
}}

.nxi-hero-badge {{
    font-size: 0.72rem;
    font-weight: 600;
    color: #dddddd;
    margin-bottom: 12px;
    display: block;
}}

.nxi-hero-overlay h2 {{
    font-size: 1.65rem;
    font-weight: 700;
    max-width: 650px;
    line-height: 1.3;
    margin: 0 0 12px 0;
    color: #ffffff;
}}

.nxi-hero-overlay p {{
    font-size: 0.88rem;
    max-width: 620px;
    line-height: 1.45;
    color: #dddddd;
    margin: 0;
    flex: 1;
}}

.nxi-btn-read {{
    align-self: flex-start;
    background-color: #ffffff;
    color: #141619;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 8px 24px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-top: 20px;
    display: inline-block;
    text-decoration: none;
    line-height: 1.4;
}}

/* ---- Articles 3-column grid ---- */
.nxi-articles-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 20px;
    width: 100%;
    box-sizing: border-box;
}}

.nxi-article-card {{
    background-color: #ffffff;
    border-radius: 4px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}}

.nxi-card-photo {{
    width: 100%;
    height: 140px;
    background-color: #e0e0e0;
    overflow: hidden;
    flex-shrink: 0;
}}

.nxi-card-photo img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}

.nxi-card-body {{
    padding: 16px;
    display: flex;
    flex-direction: column;
    flex: 1;
}}

.nxi-card-stamp {{
    font-size: 0.7rem;
    color: #777777;
    margin-bottom: 6px;
    display: block;
}}

.nxi-card-body h3 {{
    font-size: 0.95rem;
    font-weight: 700;
    color: #000000;
    margin: 0 0 8px 0;
    line-height: 1.3;
}}

.nxi-card-body p {{
    font-size: 0.8rem;
    color: #555555;
    line-height: 1.45;
    margin: 0 0 16px 0;
    flex: 1;
}}

.nxi-card-link {{
    font-size: 0.78rem;
    font-weight: 700;
    color: #000000;
    text-decoration: underline;
    cursor: pointer;
    margin-top: auto;
    display: inline-block;
}}

/* ---- Pagination ---- */
.nxi-pagination {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 16px;
    margin-top: 12px;
    font-size: 0.82rem;
    color: #555555;
    padding: 8px 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

.nxi-page-arrow {{
    width: 18px;
    height: 18px;
    display: inline-block;
    cursor: pointer;
    background: center / contain no-repeat;
    opacity: 0.7;
    vertical-align: middle;
}}

.nxi-page-arrow.nxi-left {{ background-image: url("{_ICO_CHEV_L}"); }}
.nxi-page-arrow.nxi-right {{ background-image: url("{_ICO_CHEV_R}"); }}

.nxi-page-num {{ cursor: pointer; }}
.nxi-page-num.nxi-active {{ font-weight: 700; color: #000000; }}

/* ---- Right sidebar ---- */
.nxi-sidebar-box {{
    background-color: #ffffff;
    border-radius: 4px;
    padding: 24px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

.nxi-widget-title {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #000000;
    margin: 0 0 16px 0;
}}

.nxi-users-icon {{
    width: 18px;
    height: 18px;
    background: url("{_ICO_USERS}") center / contain no-repeat;
    display: inline-block;
    flex-shrink: 0;
    vertical-align: middle;
}}

.nxi-sub-label {{
    font-size: 0.84rem;
    font-weight: 700;
    color: #333333;
    margin: 0 0 12px 0;
    display: block;
}}

.nxi-entrants-list {{
    display: flex;
    flex-direction: column;
    gap: 16px;
}}

.nxi-entrant-row {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.nxi-logo-stub {{
    width: 36px;
    height: 36px;
    min-width: 36px;
    background-color: #dddddd;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-size: 0.65rem;
    font-weight: 700;
    color: #555555;
    text-align: center;
    overflow: hidden;
    line-height: 1.1;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

.nxi-logo-stub.nxi-branded {{
    background-color: #ffffff;
    border: 1px solid #eeeeee;
}}

.nxi-entrant-meta {{
    display: flex;
    flex-direction: column;
    min-width: 0;
    flex: 1;
}}

.nxi-entrant-meta h4 {{
    font-size: 0.86rem;
    font-weight: 700;
    color: #111111;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0;
}}

.nxi-entrant-meta span {{
    font-size: 0.78rem;
    color: #666666;
    margin-top: 2px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}}

.nxi-pin-icon {{
    width: 11px;
    height: 11px;
    min-width: 11px;
    background: url("{_ICO_MAP_PIN}") center / contain no-repeat;
    display: inline-block;
    flex-shrink: 0;
}}

/* Sidebar month/year selects inside right column */
.st-key-nxi_sidebar_selects [data-testid="stSelectbox"] label {{
    display: none !important;
}}

.st-key-nxi_sidebar_selects [data-testid="stSelectbox"] [data-testid="stSelectboxRootElement"] {{
    border: 1px solid #cccccc !important;
    border-radius: 4px !important;
    background-color: #ffffff !important;
    height: 36px !important;
    box-shadow: none !important;
    min-height: 0 !important;
    margin-bottom: 2px !important;
}}

.st-key-nxi_sidebar_selects [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    padding: 0 12px !important;
    font-size: 0.84rem !important;
    color: #333333 !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
}}

/* Streamlit element containers inside columns — remove default padding */
.st-key-nxi_page_wrap [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {{
    gap: 8px !important;
}}
</style>
"""


# ---------------------------------------------------------------------------
# HTML builder helpers
# ---------------------------------------------------------------------------

def _hero_html(article: dict) -> str:
    img = html_lib.escape(article.get("image_url", ""))
    badge = html_lib.escape(article.get("timestamp", ""))
    title = html_lib.escape(article.get("title", ""))
    summary = html_lib.escape(article.get("summary", ""))
    return f"""
<article class="nxi-hero-banner">
  <img class="nxi-hero-img" src="{img}" alt="">
  <div class="nxi-hero-overlay">
    <span class="nxi-hero-badge">{badge}</span>
    <h2>{title}</h2>
    <p>{summary}</p>
    <span class="nxi-btn-read">Read</span>
  </div>
</article>
"""


def _article_card_html(article: dict) -> str:
    img = html_lib.escape(article.get("image_url", ""))
    stamp = html_lib.escape(article.get("timestamp", ""))
    title = html_lib.escape(article.get("title", ""))
    summary = html_lib.escape(article.get("summary", ""))
    return f"""
<div class="nxi-article-card">
  <div class="nxi-card-photo"><img src="{img}" alt=""></div>
  <div class="nxi-card-body">
    <span class="nxi-card-stamp">{stamp}</span>
    <h3>{title}</h3>
    <p>{summary}</p>
    <span class="nxi-card-link">Read</span>
  </div>
</div>
"""


def _articles_grid_html(articles: list[dict]) -> str:
    if not articles:
        return ""
    cards = "".join(_article_card_html(a) for a in articles)
    return f'<div class="nxi-articles-grid">{cards}</div>'


def _pagination_html() -> str:
    return f"""
<div class="nxi-pagination">
  <span class="nxi-page-arrow nxi-left"></span>
  <span class="nxi-page-num nxi-active">1</span>
  <span class="nxi-page-num">2</span>
  <span class="nxi-page-num">3</span>
  <span class="nxi-page-arrow nxi-right"></span>
</div>
"""


def _sidebar_header_html() -> str:
    return f"""
<div class="nxi-sidebar-box">
  <h2 class="nxi-widget-title">
    <span class="nxi-users-icon"></span>
    New entrants
  </h2>
"""


def _sidebar_entrants_html(entrants: list[dict], month: str) -> str:
    period = "This month" if month == "Month" else month
    if not entrants:
        rows = '<p style="font-size:0.8rem;color:#777777;margin:0;">No entrants for this period.</p>'
    else:
        rows_parts = []
        for e in entrants:
            name = html_lib.escape(e["name"])
            region = html_lib.escape(e["region"])
            if e.get("branded") == "true":
                logo = (
                    '<span style="color:#056133;font-size:0.55rem;font-weight:800;">Feu</span>'
                    '<span style="color:#9e0b0f;font-size:0.55rem;font-weight:800;">Vert</span>'
                )
                logo_cls = "nxi-logo-stub nxi-branded"
            else:
                initials = html_lib.escape((e.get("logo_text") or e["name"])[:3].upper())
                logo = initials
                logo_cls = "nxi-logo-stub"
            rows_parts.append(f"""
<div class="nxi-entrant-row">
  <div class="{logo_cls}">{logo}</div>
  <div class="nxi-entrant-meta">
    <h4>{name}</h4>
    <span><span class="nxi-pin-icon"></span>{region}</span>
  </div>
</div>""")
        rows = "".join(rows_parts)

    return f"""
  <span class="nxi-sub-label">{html_lib.escape(period)}</span>
  <div class="nxi-entrants-list">{rows}</div>
</div>
"""


# ---------------------------------------------------------------------------
# Publication request dialog
# ---------------------------------------------------------------------------
@st.dialog("Request Publication", width="medium")
def _show_publication_dialog() -> None:
    st.write("Submit your corporate news or case study for publishing on NEXUS Network Insights.")
    title_in = st.text_input("Article Title", placeholder="e.g. Bosch expands regional distribution hub...")
    st.selectbox("Category", ["Strategy", "Partnership", "Product Launch", "Sustainability", "General News"])
    st.text_area("Brief Summary", placeholder="One-sentence recap...")
    st.text_area("Full Article Content", placeholder="Write the full article here...", height=200)
    if st.button("Submit Request", type="primary", use_container_width=True):
        if not title_in.strip():
            st.error("Please fill in the Title field.")
        else:
            st.success("Publication request submitted! Our editorial team will review it shortly.")


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------
def render_news_insights() -> None:
    """Render the full News & Insights page matching nexus-news.html 1-to-1."""

    # ---- Session state ----
    for key, default in [
        ("nxi_active_tab", "nexus"),
        ("nxi_category", "Select a category"),
        ("nxi_month", "Month"),
        ("nxi_year", "Year"),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    act_tab = st.session_state.nxi_active_tab
    act_cat = st.session_state.nxi_category
    act_month = st.session_state.nxi_month
    act_year = st.session_state.nxi_year

    # ---- Data ----
    tab_articles = [a for a in NEWS_ARTICLES if a["tab"] == act_tab]
    categories = ["Select a category"] + sorted({a["category"] for a in tab_articles})
    if act_cat not in categories:
        act_cat = "Select a category"

    filtered = (
        tab_articles if act_cat == "Select a category"
        else [a for a in tab_articles if a["category"] == act_cat]
    )
    hero = next((a for a in filtered if a.get("is_hero")), filtered[0] if filtered else None)
    grid_articles = [a for a in filtered if not a.get("is_hero")][:6]

    entrants = [
        e for e in NEW_ENTRANTS
        if (act_month == "Month" or e["month"] == act_month)
        and (act_year == "Year" or e["year"] == act_year)
    ]

    months_list = ["Month", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    years_list = ["Year", "2024", "2025", "2026"]

    # ---- 1. Inject CSS ----
    st.markdown(_page_css(), unsafe_allow_html=True)

    # ---- 2. Page wrapper ----
    with st.container(key="nxi_page_wrap"):

        # ---- 3. Top bar: title left | publish button right ----
        top_left, top_right = st.columns([5, 1])
        with top_left:
            st.markdown('<h1 class="nxi-h1">NEXUS Network Insights</h1>', unsafe_allow_html=True)
        with top_right:
            with st.container(key="nxi_pub_btn"):
                if st.button("✏️ Request publication", key="nxi_pub_trigger", use_container_width=True):
                    _show_publication_dialog()

        # ---- 4. Nav tabs (styled as prototype tab bar) ----
        with st.container(key="nxi_nav_tabs_row"):
            tc1, tc2, tc3, _spacer = st.columns([1, 1, 1, 5], gap="small")
            with tc1:
                if st.button(
                    "NEXUS News", key="nxi_tab_btn_nexus",
                    type="primary" if act_tab == "nexus" else "secondary",
                ):
                    st.session_state.nxi_active_tab = "nexus"
                    st.session_state.nxi_category = "Select a category"
                    st.rerun()
            with tc2:
                if st.button(
                    "Member News", key="nxi_tab_btn_member",
                    type="primary" if act_tab == "member" else "secondary",
                ):
                    st.session_state.nxi_active_tab = "member"
                    st.session_state.nxi_category = "Select a category"
                    st.rerun()
            with tc3:
                if st.button(
                    "Monthly digest", key="nxi_tab_btn_digest",
                    type="primary" if act_tab == "digest" else "secondary",
                ):
                    st.session_state.nxi_active_tab = "digest"
                    st.session_state.nxi_category = "Select a category"
                    st.rerun()

        # ---- 5. Filter row ----
        with st.container(key="nxi_filter_row"):
            fc1, fc2, _fc_spacer = st.columns([2, 1, 5], gap="small")
            with fc1:
                sel_cat = st.selectbox(
                    "Category",
                    options=categories,
                    index=categories.index(act_cat) if act_cat in categories else 0,
                    key="nxi_cat_select",
                    label_visibility="collapsed",
                )
                if sel_cat != act_cat:
                    st.session_state.nxi_category = sel_cat
                    st.rerun()
            with fc2:
                if st.button("✕  Delete filters", key="nxi_clear_filter"):
                    st.session_state.nxi_category = "Select a category"
                    st.rerun()

        # ---- 6. Two-column main layout ----
        left_col, right_col = st.columns([3, 1], gap="medium")

        # LEFT: hero + 3-col articles grid + pagination
        with left_col:
            if hero:
                st.markdown(_hero_html(hero), unsafe_allow_html=True)
            if grid_articles:
                st.markdown(_articles_grid_html(grid_articles), unsafe_allow_html=True)
            if grid_articles:
                st.markdown(_pagination_html(), unsafe_allow_html=True)
            if not filtered:
                st.markdown(
                    '<p style="color:#777;font-size:0.9rem;padding:20px 0;">No articles found.</p>',
                    unsafe_allow_html=True,
                )

        # RIGHT: sidebar white card with entrants
        with right_col:
            # "New entrants" header (HTML)
            st.markdown(_sidebar_header_html(), unsafe_allow_html=True)

            # Month / Year selects (Streamlit widgets — interactive)
            with st.container(key="nxi_sidebar_selects"):
                m_sel = st.selectbox(
                    "Month",
                    options=months_list,
                    index=months_list.index(act_month) if act_month in months_list else 0,
                    key="nxi_month_select",
                    label_visibility="collapsed",
                )
                y_sel = st.selectbox(
                    "Year",
                    options=years_list,
                    index=years_list.index(act_year) if act_year in years_list else 0,
                    key="nxi_year_select",
                    label_visibility="collapsed",
                )
                if m_sel != act_month:
                    st.session_state.nxi_month = m_sel
                    st.rerun()
                if y_sel != act_year:
                    st.session_state.nxi_year = y_sel
                    st.rerun()

            # Entrants list + close sidebar box (HTML)
            st.markdown(_sidebar_entrants_html(entrants, act_month), unsafe_allow_html=True)
