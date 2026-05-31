"""NEXUS Partner Mapping — main Streamlit entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from auth.hubspot_bridge import init_hubspot_auth
from auth.session import init_session, is_partner, is_reviewer, is_admin
from pages.auth.connection import handle_sso_sign_in, render as render_connection
from theme.html_utils import render_html
from theme.layout import render_dev_controls, render_role_switcher, render_sidebar_branding, render_sidebar_nav
from theme.styles import inject_styles
from theme.tokens import PAGE_BG

HUB_PAGES = {
    "hub_dashboard": ("pages.portal.hub_dashboard", "render"),
    "member_directory": ("pages.portal.stubs", "render_member_directory"),
    "my_company": ("pages.portal.stubs", "render_my_company"),
    "about": ("pages.portal.stubs", "render_about"),
    "services": ("pages.portal.stubs", "render_services"),
    "news": ("pages.portal.stubs", "render_news"),
    "help": ("pages.portal.stubs", "render_help"),
}

PARTNER_MAPPING_PAGES = {
    "upload": ("pages.partner.upload", "render"),
    "history": ("pages.partner.history", "render"),
    "deposit_detail": ("pages.partner.deposit_detail", "render"),
    "mapping_dashboard": ("pages.partner.dashboard", "render"),
    "corrective": ("pages.partner.corrective", "render"),
}

REVIEWER_PAGES = {
    "review_queue": ("pages.internal.review_queue", "render"),
    "review_detail": ("pages.internal.review_detail", "render"),
    "bulk_review": ("pages.internal.bulk_review", "render"),
    "overlap": ("pages.internal.overlap", "render"),
    "discrepancy": ("pages.internal.discrepancy", "render"),
}

ADMIN_PAGES = {
    "admin_calibration": ("pages.admin.stubs", "render_calibration"),
    "admin_onboarding": ("pages.admin.stubs", "render_onboarding"),
    "admin_decommission": ("pages.admin.stubs", "render_decommission"),
    "admin_closure": ("pages.admin.stubs", "render_closure"),
    "admin_config": ("pages.admin.stubs", "render_system_config"),
    "admin_audit": ("pages.admin.stubs", "render_post_closure_audit"),
}


def _import_callable(module_path: str, attr: str = "render"):
    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, attr)


def _default_page() -> str:
    if is_reviewer() and not is_partner():
        return "review_queue"
    return "hub_dashboard"


def _accessible_pages() -> dict[str, tuple[str, str]]:
    pages = {}
    if is_partner():
        pages.update(HUB_PAGES)
        pages.update(PARTNER_MAPPING_PAGES)
    if is_reviewer():
        pages.update(REVIEWER_PAGES)
    if is_admin():
        pages.update(ADMIN_PAGES)

    return pages


def _render_access_denied() -> None:
    st.error("Your partner account is not active. Please contact Nexus support.")
    st.info("BR-ISO-04: Access refused when `is_active = FALSE`.")


def _render_inactive_gate() -> None:
    inject_styles()
    st.set_page_config(page_title="NEXUS — Access Denied", layout="wide")
    _render_access_denied()


def main() -> None:
    st.set_page_config(
        page_title="NEXUS — Connection",
        page_icon="▦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()
    init_hubspot_auth()

    if st.query_params.get("jwt"):
        st.session_state.authenticated = True

    if not handle_sso_sign_in():
        render_html(f"<style>.stApp {{ background-color: {PAGE_BG}; }}</style>")
        _left, center, _right = st.columns([1, 1.1, 1])
        with center:
            render_connection()
        return

    session = init_session()
    if session is None:
        _render_access_denied()
        return

    from services.brd_state import init_brd_state

    init_brd_state()

    pages = _accessible_pages()
    default = _default_page()

    if "active_page" not in st.session_state:
        st.session_state.active_page = default

    if st.session_state.active_page not in pages:
        st.session_state.active_page = default

    if st.session_state.get("navigate_to"):
        target = st.session_state.pop("navigate_to")
        if target in pages:
            st.session_state.active_page = target

    with st.sidebar:
        render_sidebar_branding()
        render_sidebar_nav(st.session_state.active_page, set(pages.keys()))
        render_dev_controls()
        render_role_switcher()

    module_path, attr = pages[st.session_state.active_page]
    render_fn = _import_callable(module_path, attr)
    render_fn(st.session_state.active_page)


if __name__ == "__main__":
    main()
