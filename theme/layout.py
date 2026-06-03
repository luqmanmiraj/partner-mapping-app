"""Sidebar layout helpers — dev controls and persona switcher."""

from __future__ import annotations

import streamlit as st

# Re-export nav registries for callers that import from layout.
from theme.sidenav import (  # noqa: F401
    ADMIN_NAV,
    HUB_PORTAL_NAV,
    HUB_PORTAL_NAV_MEMBER,
    HUB_PORTAL_NAV_SUPPLIER,
    HUB_PORTAL_SECONDARY,
    PARTNER_MAPPING_NAV,
    REVIEWER_NAV,
)


def render_sidebar_branding() -> None:
    """Branding is rendered inside :func:`theme.sidenav.render_sidenav`."""


def render_sidebar_nav(active_page: str, accessible_pages: set[str] | None = None) -> None:
    """Navigation is rendered inside :func:`theme.sidenav.render_sidenav`."""


def render_app_top_header(display_name: str) -> None:
    """Top bar is rendered in :func:`streamlit_app.main` via :func:`theme.top_header.render_top_header`."""


def render_app_page_content(render_fn, *args, **kwargs) -> None:
    """Page body is wrapped in :func:`theme.page_content.render_page_content` from ``streamlit_app.main``."""


def render_dev_controls() -> tuple[bool, str]:
    """Dev-only sidebar controls (hidden in the UI via sidenav CSS)."""
    with st.container(key="dev_controls"):
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
    """Dev-only persona switcher (rendered under sidebar logo)."""
    options = {
        "Supplier — MEYLE": ("11111111", "partner"),
        "Supplier — HELLA": ("44444444", "partner"),
        "Member — DE": ("66666601", "partner"),
        "Reviewer": ("reviewer", "reviewer"),
        "Admin": ("admin", "admin"),
    }
    with st.container(key="sidenav_persona"):
        current = st.session_state.get("dev_persona", "Supplier — MEYLE")
        st.caption("Persona")
        choice = st.selectbox(
            "Persona",
            list(options.keys()),
            index=list(options.keys()).index(current) if current in options else 0,
            label_visibility="collapsed",
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
