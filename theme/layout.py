"""Sidebar layout and dev controls."""

from __future__ import annotations

import html

import streamlit as st

from auth.session import get_session, is_admin, is_partner, is_reviewer
from theme.html_utils import render_html


HUB_PORTAL_NAV = [
    ("Dashboard", "hub_dashboard", "▦"),
    ("Member Directory", "member_directory", "👥"),
    ("My Company", "my_company", "🏢"),
]

HUB_PORTAL_SECONDARY = [
    ("About", "about", ""),
    ("Services", "services", ""),
    ("News & Insights", "news", ""),
    ("Help & Support Center", "help", ""),
]

PARTNER_MAPPING_NAV = [
    ("Upload", "upload", "📤"),
    ("Deposit History", "history", "📋"),
    ("Financial Dashboard", "mapping_dashboard", "📊"),
    ("Corrective Deposit", "corrective", "✏️"),
]

REVIEWER_NAV = [
    ("Review Queue", "review_queue", "📝"),
    ("Granular Review", "review_detail", "🔍"),
    ("Bulk Review", "bulk_review", "📦"),
    ("Overlap Investigation", "overlap", "🔗"),
    ("Discrepancy Screen", "discrepancy", "⚖️"),
]

ADMIN_NAV = [
    ("Calibration", "admin_calibration", "⚙️"),
    ("Onboarding", "admin_onboarding", "➕"),
    ("Decommission", "admin_decommission", "⛔"),
    ("Closure", "admin_closure", "🔒"),
    ("System Config", "admin_config", "🎛"),
    ("Post-Closure Audit", "admin_audit", "📋"),
]


def render_sidebar_branding() -> None:
    render_html(
        """
        <div class="nexus-logo">
            <span class="mark">N!</span> NEXUS
        </div>
        """
    )


def _nav_button(label: str, page_id: str, icon: str, active_page: str, accessible: set[str]) -> None:
    if page_id not in accessible:
        return
    prefix = f"{icon} " if icon else ""
    is_active = page_id == active_page
    if st.button(
        f"{prefix}{label}",
        key=f"nav_{page_id}",
        use_container_width=True,
        type="primary" if is_active else "secondary",
    ):
        if not is_active:
            st.session_state.active_page = page_id
            st.rerun()


def _nav_section(title: str) -> None:
    render_html(f'<div class="nav-section">{html.escape(title)}</div>')


def render_sidebar_nav(active_page: str, accessible_pages: set[str] | None = None) -> None:
    session = get_session()
    accessible = accessible_pages or set()

    if is_partner():
        for label, page_id, icon in HUB_PORTAL_NAV:
            _nav_button(label, page_id, icon, active_page, accessible)
        _nav_section("Nexus Automotive")
        for label, page_id, icon in HUB_PORTAL_SECONDARY:
            _nav_button(label, page_id, icon, active_page, accessible)
        _nav_section("Partner Mapping")
        for label, page_id, icon in PARTNER_MAPPING_NAV:
            _nav_button(label, page_id, icon, active_page, accessible)
    elif is_reviewer() and not is_partner():
        _nav_section("Internal Cockpit")
        for label, page_id, icon in REVIEWER_NAV:
            _nav_button(label, page_id, icon, active_page, accessible)

    if is_admin():
        _nav_section("Admin")
        for label, page_id, icon in ADMIN_NAV:
            _nav_button(label, page_id, icon, active_page, accessible)

    render_html(
        f"""
        <div class="account-row">
            <span>👤 {html.escape(session.display_name)}</span>
            <span>⌃</span>
        </div>
        """
    )


def render_dev_controls() -> tuple[bool, str]:
    st.divider()
    st.caption("Developer controls")
    use_snowflake = st.toggle(
        "Use Snowflake data",
        value=st.session_state.get("use_snowflake", False),
    )
    passcode = st.text_input(
        "TOTP passcode",
        value=st.session_state.get("passcode", ""),
        type="password",
    )
    st.session_state.use_snowflake = use_snowflake
    st.session_state.passcode = passcode
    return use_snowflake, passcode


def render_role_switcher() -> None:
    """Dev-only persona switcher for local testing."""
    st.divider()
    st.caption("Dev persona")
    options = {
        "Supplier — MEYLE": ("11111111", "partner"),
        "Supplier — HELLA": ("44444444", "partner"),
        "Member — DE": ("66666601", "partner"),
        "Reviewer": ("reviewer", "reviewer"),
        "Admin": ("admin", "admin"),
    }
    current = st.session_state.get("dev_persona", "Supplier — MEYLE")
    choice = st.selectbox(
        "Switch persona",
        list(options.keys()),
        index=list(options.keys()).index(current) if current in options else 0,
    )
    if choice != current:
        st.session_state.dev_persona = choice
        key, role_type = options[choice]
        if role_type == "partner":
            st.session_state.hubspot_company_id = key
        st.session_state.app_role = role_type
        st.session_state.pop("user_session", None)
        st.session_state.pop("active_page", None)
        st.session_state.pop("navigate_to", None)
        st.rerun()
