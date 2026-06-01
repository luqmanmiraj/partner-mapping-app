"""Sidebar navigation — matches .prototype/sidenav.html (Streamlit buttons as nav links)."""

from __future__ import annotations

import base64
import html
import mimetypes

import streamlit as st

from auth.session import get_session, is_admin, is_partner, is_reviewer
from theme.html_utils import render_html
from theme.paths import image_path, nav_icon_path

_PREFIX = "nexus-sidenav"

HUB_PORTAL_NAV = [
    ("Dashboard", "hub_dashboard", ""),
    ("Member Directory", "member_directory", ""),
    ("My Company", "my_company", ""),
]

HUB_PORTAL_SECONDARY = [
    ("About", "about", ""),
    ("Services", "services", ""),
    ("News & Insights", "news", ""),
    ("Help & Support Center", "help", ""),
]

PARTNER_MAPPING_NAV = [
    ("Upload", "upload", ""),
    ("Deposit History", "history", ""),
    ("Financial Dashboard", "mapping_dashboard", ""),
    ("Corrective Deposit", "corrective", ""),
]

REVIEWER_NAV = [
    ("Review Queue", "review_queue", ""),
    ("Granular Review", "review_detail", ""),
    ("Bulk Review", "bulk_review", ""),
    ("Overlap Investigation", "overlap", ""),
    ("Discrepancy Screen", "discrepancy", ""),
]

ADMIN_NAV = [
    ("Calibration", "admin_calibration", ""),
    ("Onboarding", "admin_onboarding", ""),
    ("Decommission", "admin_decommission", ""),
    ("Closure", "admin_closure", ""),
    ("System Config", "admin_config", ""),
    ("Post-Closure Audit", "admin_audit", ""),
]

_LOGO_FILE = "side-nav-logo.jpg"

_NAV_ICON_FILES: dict[str, str] = {
    "hub_dashboard": "dashboard-nav-icon.svg",
    "member_directory": "member-directory-nav-icon.svg",
    "my_company": "my-company-nav-icon.svg",
    "about": "about-nav-icon.svg",
    "services": "services-nav-icon.svg",
    "news": "news-insights-nav-icon.svg",
    "help": "help-support-nav-icon.svg",
}

_ALL_NAV_PAGE_IDS: set[str] = {
    page_id
    for group in (
        HUB_PORTAL_NAV,
        HUB_PORTAL_SECONDARY,
        PARTNER_MAPPING_NAV,
        REVIEWER_NAV,
        ADMIN_NAV,
    )
    for _, page_id, _ in group
}


def _nav_icon_css_rules() -> str:
    """Per-item ::before icons via st.container(key='nav_<page_id>') class hooks."""
    rules: list[str] = []
    for page_id in sorted(_ALL_NAV_PAGE_IDS):
        filename = _NAV_ICON_FILES.get(page_id)
        uri = _file_data_uri(nav_icon_path(filename)) if filename else None
        selector = f'section[data-testid="stSidebar"] .st-key-nav_{page_id} button::before'
        if uri:
            rules.append(
                f"""
                {selector} {{
                    content: "";
                    display: inline-block;
                    width: 18px;
                    height: 18px;
                    margin-right: 12px;
                    flex-shrink: 0;
                    background-color: #ffffff;
                    mask: url("{uri}") center / contain no-repeat;
                    -webkit-mask: url("{uri}") center / contain no-repeat;
                    transition: background-color 0.2s ease;
                }}
                """
            )
        else:
            rules.append(
                f"""
                {selector} {{
                    content: "";
                    display: inline-block;
                    width: 18px;
                    height: 18px;
                    margin-right: 12px;
                    flex-shrink: 0;
                }}
                """
            )
    return "\n".join(rules)


def sidenav_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                Helvetica, Arial, sans-serif;
            color: #ffffff;
            margin: -1rem -1rem 0 -1rem;
            padding-top: 16px;
            width: 100%;
            position: relative;
        }}

        section[data-testid="stSidebar"] .{p}__section-heading {{
            font-size: 13px;
            font-weight: 700;
            color: #555555;
            padding: 10px 20px 4px 20px;
            letter-spacing: 0.4px;
            margin: 0;
            text-transform: none;
        }}

        .{p} .account {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 20px;
            border-top: 1px solid #333333;
            margin-top: 16px;
            color: #ffffff;
            font-size: 13px;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: #111111;
            padding-top: 0;
        }}

        /* Header row: logo left, logout right (prototype .sidebar-header) */
        section[data-testid="stSidebar"] .st-key-sidenav_header {{
            width: 100% !important;
            padding: 0 20px !important;
            margin: 0 0 20px 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_header [data-testid="stHorizontalBlock"] {{
            align-items: center !important;
            gap: 0 !important;
            width: 100% !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_header [data-testid="column"]:first-child {{
            min-width: 0 !important;
            flex: 1 1 auto !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_header [data-testid="column"]:last-child {{
            flex: 0 0 auto !important;
            display: flex !important;
            justify-content: flex-end !important;
            align-items: center !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_header .logo {{
            height: 32px;
            width: auto;
            max-width: 150px;
            object-fit: contain;
            object-position: left;
            display: block;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_header button {{
            width: auto !important;
            min-height: 32px !important;
            height: 32px !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            background: transparent !important;
            color: #ffffff !important;
            opacity: 0.8;
            transition: opacity 0.2s ease;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_header button:hover {{
            opacity: 1 !important;
            background: transparent !important;
            color: #ffffff !important;
            border: none !important;
        }}

        /* Nav rows: one Streamlit button per item (prototype .nav-link look) */
        section[data-testid="stSidebar"] [class*="st-key-nav_"] {{
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            gap: 0 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button {{
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 100% !important;
            padding: 10px 20px !important;
            margin: 0 !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            line-height: 1.3 !important;
            min-height: 0 !important;
            height: auto !important;
            background: transparent !important;
            color: #ffffff !important;
            transition: background-color 0.2s ease, color 0.2s ease !important;
        }}

        /* Active item (prototype .nav-item.active .nav-link) — black icon + bold text */
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] {{
            background-color: #f79400 !important;
            color: #000000 !important;
            font-weight: 700 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"]::before {{
            background-color: #000000 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] > span,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] > div,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"] p {{
            color: #000000 !important;
            font-weight: 700 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"]:hover {{
            background-color: #f79400 !important;
            color: #000000 !important;
            border: none !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"]:hover::before {{
            background-color: #000000 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"]:hover > span,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"]:hover > div,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="primary"]:hover p {{
            color: #000000 !important;
        }}

        /* Hover for inactive links (prototype .nav-item:not(.active) .nav-link:hover) */
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:hover,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:hover {{
            background-color: #1a1a1a !important;
            color: #f79400 !important;
            border: none !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:hover::before,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:hover::before {{
            background-color: #f79400 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:focus,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:focus-visible,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:focus,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:focus-visible {{
            background-color: #1a1a1a !important;
            color: #f79400 !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:focus::before,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:focus-visible::before,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:focus::before,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:focus-visible::before {{
            background-color: #f79400 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button > span,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:hover > span,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="tertiary"]:hover > div,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:hover > span,
        section[data-testid="stSidebar"] [class*="st-key-nav_"] button[kind="secondary"]:hover > div {{
            background: transparent !important;
            color: #f79400 !important;
        }}

        {_nav_icon_css_rules()}
    """


def inject_sidenav_styles() -> None:
    render_html(f"<style>{sidenav_styles()}</style>")


def _file_data_uri(path) -> str | None:
    if not path.is_file():
        return None
    raw = path.read_bytes()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    if mime == "image/svg+xml" or path.suffix.lower() == ".svg":
        mime = "image/svg+xml"
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _logo_data_uri() -> str | None:
    return _file_data_uri(image_path(_LOGO_FILE))


def _render_nav_link(page_id: str, label: str, active_page: str) -> None:
    is_active = page_id == active_page
    btn_type = "primary" if is_active else "tertiary"
    with st.container(key=f"nav_{page_id}"):
        if st.button(
            label,
            key=f"navbtn_{page_id}",
            type=btn_type,
            use_container_width=True,
        ):
            if not is_active:
                st.session_state.active_page = page_id
                st.rerun()


def _nav_section(
    items: list[tuple[str, str, str]],
    active_page: str,
    accessible: set[str],
) -> None:
    visible = [(label, page_id) for label, page_id, _ in items if page_id in accessible]
    for label, page_id in visible:
        _render_nav_link(page_id, label, active_page)


def _sign_out() -> None:
    for key in (
        "authenticated",
        "sso_clicked",
        "user_session",
        "active_page",
        "navigate_to",
        "jwt_token",
    ):
        st.session_state.pop(key, None)


def _section_heading(title: str) -> None:
    render_html(
        f'<p class="{_PREFIX}__section-heading">{html.escape(title)}</p>'
    )


def handle_sidenav_query(accessible_pages: set[str]) -> None:
    nav = st.query_params.get("nav")
    if nav and nav in accessible_pages:
        st.session_state.active_page = nav
        try:
            del st.query_params["nav"]
        except Exception:
            pass
        st.rerun()


def render_sidenav(active_page: str, accessible_pages: set[str]) -> None:
    session = get_session()
    p = _PREFIX
    accessible = accessible_pages

    logo_uri = _logo_data_uri()
    logo_html = (
        f'<img class="logo" src="{logo_uri}" alt="NEXUS" />'
        if logo_uri
        else f'<span>{html.escape("NEXUS")}</span>'
    )

    render_html(f'<div class="{p}">')

    with st.container(key="sidenav_header"):
        logo_col, logout_col = st.columns([5, 1], gap="small")
        with logo_col:
            render_html(f'<div class="sidebar-header-logo">{logo_html}</div>')
        with logout_col:
            if st.button(
                "",
                key="navbtn_logout",
                help="Sign out",
                icon=":material/logout:",
                type="tertiary",
            ):
                _sign_out()
                st.rerun()

    enterprise_label = session.display_name or "Enterprise"
    _section_heading(enterprise_label)

    if is_partner():
        _nav_section(HUB_PORTAL_NAV, active_page, accessible)
        _section_heading("NEXUS Automotive")
        _nav_section(HUB_PORTAL_SECONDARY, active_page, accessible)
        _section_heading("Partner Mapping")
        _nav_section(PARTNER_MAPPING_NAV, active_page, accessible)
    elif is_reviewer() and not is_partner():
        _section_heading("Internal Cockpit")
        _nav_section(REVIEWER_NAV, active_page, accessible)

    if is_admin():
        _section_heading("Admin")
        _nav_section(ADMIN_NAV, active_page, accessible)

    render_html(
        f"""
        <div class="account">
            <span>👤 {html.escape(session.display_name)}</span>
            <span aria-hidden="true">⌃</span>
        </div>
        </div>
        """
    )
    render_html(account_widget_html)
