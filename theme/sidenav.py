"""Sidebar navigation — matches .prototype/sidenav.html (Streamlit buttons as nav links)."""

from __future__ import annotations

import base64
import html
import mimetypes

import streamlit as st
import streamlit.components.v1 as components

from auth.session import get_session, is_admin, is_partner, is_reviewer
from theme.html_utils import render_html
from theme.paths import image_path, nav_icon_path

_PREFIX = "nexus-sidenav"
_SIDENAV_WIDTH = "280px"
# Column ratio for Persona row (label left, dropdown right)
_SIDENAV_TOP_COL_RATIO = (1, 1.7)
# Compact top: 16px pad + 48px logo + 8px gap + 32px persona row + 8px pad
_SIDENAV_TOP_FIXED_HEIGHT = "160px"

HUB_PORTAL_NAV_SUPPLIER = [
    ("Dashboard", "hub_dashboard", ""),
    ("Member Directory", "member_directory", ""),
    ("My Company", "my_company", ""),
]

HUB_PORTAL_NAV_MEMBER = [
    ("Dashboard", "hub_dashboard", ""),
    ("Offers", "offers", ""),
    ("Supplier Portfolio", "supplier_portfolio", ""),
    ("My Company", "my_company", ""),
]

# Back-compat alias for imports from theme.layout
HUB_PORTAL_NAV = HUB_PORTAL_NAV_SUPPLIER

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
    "offers": "offers-nav-icon.svg",
    "supplier_portfolio": "supplier-portfolio-nav-icon.svg",
    "my_company": "my-company-nav-icon.svg",
    "about": "about-nav-icon.svg",
    "services": "services-nav-icon.svg",
    "news": "news-insights-nav-icon.svg",
    "help": "help-support-nav-icon.svg",
    "upload": "upload-nav-icon.svg",
    "history": "deposit-history-nav-icon.svg",
    "mapping_dashboard": "financial-dashboard-nav-icon.svg",
    "corrective": "corrective-deposit-nav-icon.svg",
    "review_queue": "review-queue-nav-icon.svg",
    "review_detail": "granular-review-nav-icon.svg",
    "bulk_review": "bulk-review-nav-icon.svg",
    "overlap": "overlap-investigation-nav-icon.svg",
    "discrepancy": "discrepancy-screen-nav-icon.svg",
    "admin_calibration": "admin-calibration-nav-icon.svg",
    "admin_onboarding": "admin-onboarding-nav-icon.svg",
    "admin_decommission": "admin-decommission-nav-icon.svg",
    "admin_closure": "admin-closure-nav-icon.svg",
    "admin_config": "admin-config-nav-icon.svg",
    "admin_audit": "admin-audit-nav-icon.svg",
}

_ALL_NAV_PAGE_IDS: set[str] = {
    page_id
    for group in (
        HUB_PORTAL_NAV_SUPPLIER,
        HUB_PORTAL_NAV_MEMBER,
        HUB_PORTAL_SECONDARY,
        PARTNER_MAPPING_NAV,
        REVIEWER_NAV,
        ADMIN_NAV,
    )
    for _, page_id, _ in group
}

_MEMBER_ONLY_PAGE_IDS = frozenset({"offers", "supplier_portfolio"})
_SUPPLIER_ONLY_PAGE_IDS = frozenset({"member_directory"})


def hub_portal_nav_for_session(session) -> list[tuple[str, str, str]]:
    """Hub portal primary nav items depend on partner declarant type (member vs supplier)."""
    if getattr(session, "declarant_type", "") == "member":
        return list(HUB_PORTAL_NAV_MEMBER)
    return list(HUB_PORTAL_NAV_SUPPLIER)


def remap_active_page_for_declarant(active_page: str, declarant_type: str) -> str:
    """When switching persona, map unavailable pages to a sensible default."""
    if declarant_type == "member" and active_page in _SUPPLIER_ONLY_PAGE_IDS:
        return "offers"
    if declarant_type != "member" and active_page in _MEMBER_ONLY_PAGE_IDS:
        return "member_directory"
    return active_page

# Single width for every sidebar nav icon (24px wide SVG assets).
_NAV_ICON_SIZE = "24px"
_NAV_ICON_MARGIN_RIGHT = "12px"


def _nav_icon_base_selector() -> str:
    """All nav rows use st.button(key='navbtn_<page_id>')."""
    return 'section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button::before'


def _nav_icon_base_css() -> str:
    """Shared ::before box — size, spacing, and mask color for every menu item."""
    sel = _nav_icon_base_selector()
    return f"""
        {sel} {{
            content: "";
            display: inline-block;
            width: {_NAV_ICON_SIZE};
            height: auto;
            min-width: {_NAV_ICON_SIZE};
            min-height: {_NAV_ICON_SIZE};
            margin-right: {_NAV_ICON_MARGIN_RIGHT};
            flex-shrink: 0;
            background-color: #ffffff;
            transition: background-color 0.2s ease;
        }}
    """


def _nav_icon_mask_css_rules() -> str:
    """Per-page SVG mask only (dimensions come from :func:`_nav_icon_base_css`)."""
    rules: list[str] = []
    for page_id in sorted(_ALL_NAV_PAGE_IDS):
        filename = _NAV_ICON_FILES.get(page_id)
        if not filename:
            continue
        uri = _file_data_uri(nav_icon_path(filename))
        if not uri:
            continue
        selector = f'section[data-testid="stSidebar"] .st-key-navbtn_{page_id} button::before'
        rules.append(
            f"""
            {selector} {{
                mask: url("{uri}") center / contain no-repeat;
                -webkit-mask: url("{uri}") center / contain no-repeat;
            }}
            """
        )
    return "\n".join(rules)


def _nav_icon_css_rules() -> str:
    return _nav_icon_base_css() + _nav_icon_mask_css_rules()


def sidenav_styles() -> str:
    p = _PREFIX
    return f"""
        /* Sidebar shell (no separate wrapper div — avoids empty st.html block) */
        section[data-testid="stSidebar"] > div {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                Helvetica, Arial, sans-serif;
            color: #ffffff;
            margin: -1rem -1rem 0 -1rem;
            padding-top: 0;
            width: 100%;
            position: relative;
        }}

        /* Scrollable nav area; room above fixed account footer */
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            overflow-y: auto !important;
            overflow-x: hidden !important;
            max-height: 100vh !important;
            height: 100% !important;
            padding-bottom: 140px !important;
            box-sizing: border-box;
            -webkit-overflow-scrolling: touch;
        }}

        /* Fixed top shell — one div wrapping logo + Persona switcher */
        section[data-testid="stSidebar"] .{p}__top-fixed {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            z-index: 110 !important;
            width: {_SIDENAV_WIDTH} !important;
            height: {_SIDENAV_TOP_FIXED_HEIGHT} !important;
            max-height: {_SIDENAV_TOP_FIXED_HEIGHT} !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
            border-bottom: 1px solid #333333 !important;
            background-color: #111111 !important;
            box-sizing: border-box !important;
            overflow: visible !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_top_fixed {{
            width: 100% !important;
            height: 100% !important;
            max-height: 100% !important;
            margin: 0 !important;
            padding: 16px 0 3px 0 !important;
            gap: 6px !important;
            border: none !important;
            background-color: #111111 !important;
            box-sizing: border-box !important;
            overflow: visible !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: flex-start !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_top_fixed [data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] .st-key-sidenav_top_fixed [data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: #111111 !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* Scrollable menu — offset below fixed top block */
        section[data-testid="stSidebar"] .st-key-sidenav_nav_body {{
            padding-top: {_SIDENAV_TOP_FIXED_HEIGHT} !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
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

        section[data-testid="stSidebar"] .{p}__account {{
            position: fixed;
            left: 0;
            width: {_SIDENAV_WIDTH};
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 20px;
            border-top: 1px solid #333333;
            margin: 0;
            color: #ffffff;
            font-size: 13px;
            background-color: #111111;
            z-index: 100;
            box-sizing: border-box;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: #111111;
            padding-top: 0;
        }}

        /* Header row: logo only */
        section[data-testid="stSidebar"] .st-key-sidenav_header {{
            width: 100% !important;
            padding: 0 16px !important;
            margin: 0 0 6px 0 !important;
            flex-shrink: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_header .logo {{
            height: 48px;
            width: auto;
            max-width: none;
            object-fit: contain;
            object-position: left;
            display: block;
        }}

        /* Persona switcher — two rows (label + full-width dropdown) */
        section[data-testid="stSidebar"] .st-key-sidenav_persona {{
            width: 100% !important;
            padding: 0 16px 12px 16px !important;
            margin: 0 !important;
            flex-shrink: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona hr {{
            display: none !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stHorizontalBlock"] {{
            display: block !important;
            width: 100% !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stVerticalBlock"],
        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stVerticalBlockBorderWrapper"] {{
            gap: 0 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stVerticalBlock"] > div,
        section[data-testid="stSidebar"] .st-key-sidenav_persona .stElementContainer {{
            margin: 0 !important;
            padding: 0 !important;
        }}

        section[data-testid="stSidebar"] .{p}__persona-label {{
            font-size: 11px !important;
            line-height: 1.2 !important;
            color: #888888 !important;
            font-weight: 500 !important;
            white-space: nowrap !important;
            display: block !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stCaptionContainer"],
        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stCaptionContainer"] p,
        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stCaptionContainer"] [data-testid="stMarkdownContainer"] {{
            margin: 0 !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
            min-height: 0 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stVerticalBlock"] > div:first-child,
        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stVerticalBlock"] > div:first-child .stElementContainer {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stCaption"] {{
            font-size: 11px !important;
            line-height: 1 !important;
            color: #888888 !important;
            font-weight: 500 !important;
            margin: 0 !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stSelectbox"] {{
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stSelectbox"] > div {{
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-testid="stSelectbox"] label {{
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"] {{
            width: 100% !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"],
        section[data-testid="stSidebar"] .st-key-sidenav_persona div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"] .st-key-sidenav_persona [role="combobox"] {{
            background-color: #1a1a1a !important;
            border: 1px solid #333333 !important;
            border-radius: 4px !important;
            color: #e5e5e5 !important;
            font-size: 11px !important;
            line-height: 1.35 !important;
            min-height: 32px !important;
            height: 32px !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"] > div {{
            min-height: 32px !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"] span,
        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"] div,
        section[data-testid="stSidebar"] .st-key-sidenav_persona [role="combobox"] span {{
            font-size: 11px !important;
            line-height: 1.35 !important;
            color: #e5e5e5 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"] [value="value"],
        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"] input {{
            font-size: 11px !important;
            line-height: 1.35 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"]:hover,
        section[data-testid="stSidebar"] .st-key-sidenav_persona div[data-baseweb="select"] > div:hover {{
            border-color: #444444 !important;
            background-color: #222222 !important;
        }}

        section[data-testid="stSidebar"] .st-key-sidenav_persona [data-baseweb="select"] svg {{
            width: 12px !important;
            height: 12px !important;
            fill: #b0b0b0 !important;
        }}

        /* Hide empty st.html fragments in the sidebar */
        section[data-testid="stSidebar"] [data-testid="stHtml"]:empty {{
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        /* Nav rows: one Streamlit button per item (prototype .nav-link look) */
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] {{
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            gap: 0 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button {{
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
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"] {{
            background-color: #f79400 !important;
            color: #000000 !important;
            font-weight: 700 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"]::before {{
            background-color: #000000 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"] > span,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"] > div,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"] p {{
            color: #000000 !important;
            font-weight: 700 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"]:hover {{
            background-color: #f79400 !important;
            color: #000000 !important;
            border: none !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"]:hover::before {{
            background-color: #000000 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"]:hover > span,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"]:hover > div,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="primary"]:hover p {{
            color: #000000 !important;
        }}

        /* Hover for inactive links (prototype .nav-item:not(.active) .nav-link:hover) */
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:hover,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:hover {{
            background-color: #1a1a1a !important;
            color: #f79400 !important;
            border: none !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:hover::before,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:hover::before {{
            background-color: #f79400 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:focus,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:focus-visible,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:focus,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:focus-visible {{
            background-color: #1a1a1a !important;
            color: #f79400 !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:focus::before,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:focus-visible::before,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:focus::before,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:focus-visible::before {{
            background-color: #f79400 !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button > span,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:hover > span,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="tertiary"]:hover > div,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:hover > span,
        section[data-testid="stSidebar"] [class*="st-key-navbtn_"] button[kind="secondary"]:hover > div {{
            background: transparent !important;
            color: #f79400 !important;
        }}

        /* Developer controls + TOTP passcode (sidebar cleanup) */
        section[data-testid="stSidebar"] .st-key-dev_controls {{
            display: none !important;
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
    if st.button(
        label,
        key=f"navbtn_{page_id}",
        type=btn_type,
        width="stretch",
    ):
        if not is_active:
            st.session_state.active_page = page_id
            st.rerun()


def _nav_sections_for_session(session) -> list[tuple[str, list[tuple[str, str, str]]]]:
    """Sidebar sections for the current persona (headings + nav rows)."""
    sections: list[tuple[str, list[tuple[str, str, str]]]] = []
    if is_partner():
        sections.append((session.display_name or "Enterprise", hub_portal_nav_for_session(session)))
        sections.append(("NEXUS Automotive", HUB_PORTAL_SECONDARY))
        sections.append(("Partner Mapping", PARTNER_MAPPING_NAV))
    elif is_reviewer():
        sections.append(("Internal Cockpit", REVIEWER_NAV))
    if is_admin():
        sections.append(("Admin", ADMIN_NAV))
    return sections


def _render_nav_sections(
    sections: list[tuple[str, list[tuple[str, str, str]]]],
    active_page: str,
    accessible: set[str],
) -> None:
    """Render nav links once per page_id across all sections."""
    rendered_ids: set[str] = set()
    for heading, items in sections:
        visible = [(label, page_id) for label, page_id, _ in items if page_id in accessible]
        if not visible:
            continue
        _section_heading(heading)
        for label, page_id in visible:
            if page_id in rendered_ids:
                continue
            rendered_ids.add(page_id)
            _render_nav_link(page_id, label, active_page)


def _section_heading(title: str) -> None:
    render_html(
        f'<p class="{_PREFIX}__section-heading">{html.escape(title)}</p>'
    )


def _bind_sidenav_top_fixed_shell() -> None:
    """Wrap logo + persona Streamlit block in a single fixed-height HTML div."""
    p = _PREFIX
    components.html(
        f"""
        <script>
        (function () {{
            const doc = window.parent.document;
            const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
            if (!sidebar) return;
            function bind() {{
                const block = sidebar.querySelector(".st-key-sidenav_top_fixed");
                if (!block) return;
                let shell = sidebar.querySelector(".{p}__top-fixed");
                if (!shell) {{
                    shell = doc.createElement("div");
                    shell.className = "{p}__top-fixed";
                    shell.setAttribute("data-sidenav-top", "fixed");
                    block.parentNode.insertBefore(shell, block);
                }}
                if (block.parentElement !== shell) {{
                    shell.appendChild(block);
                }}
            }}
            bind();
            setTimeout(bind, 0);
            setTimeout(bind, 150);
        }})();
        </script>
        """,
        height=0,
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

    with st.container(key="sidenav_top_fixed"):
        with st.container(key="sidenav_header"):
            render_html(f'<div class="sidebar-header-logo">{logo_html}</div>')

        from theme.layout import render_role_switcher

        render_role_switcher()

    _bind_sidenav_top_fixed_shell()

    with st.container(key="sidenav_nav_body"):
        _render_nav_sections(_nav_sections_for_session(session), active_page, accessible)

    render_html(
        f"""
        <div class="{p}__account">
            <span>👤 {html.escape(session.display_name)}</span>
            <span aria-hidden="true">⌃</span>
        </div>
        """
    )
