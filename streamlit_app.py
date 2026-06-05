"""NEXUS Partner Mapping — main Streamlit entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

load_dotenv(APP_DIR / ".env")

from auth.hubspot_bridge import init_hubspot_auth
from auth.session import get_session, init_session, is_partner, is_reviewer, is_admin
from pages.auth.connection import (
    handle_sso_sign_in,
    render as render_connection,
    try_process_oauth_callback,
)
from services.hubspot_session import is_authenticated, show_callback_screen
from theme.layout import render_dev_controls
from theme.page_content import render_page_content
from theme.sidenav import handle_sidenav_query, remap_active_page_for_declarant, render_sidenav
from theme.styles import inject_styles
from theme.top_header import render_top_header

LOGS_PAGE = {
    "logs": ("pages.portal.logs", "render"),
}

HUB_PAGES_COMMON = {
    "hub_dashboard": ("pages.portal.hub_dashboard", "render"),
    "logs": ("pages.portal.logs", "render"),
    "my_company": ("pages.portal.my_company", "render"),
    "about": ("pages.portal.about", "render"),
    "services": ("pages.portal.services", "render"),
    "news": ("pages.portal.news", "render"),
    "help": ("pages.portal.help", "render"),
}

HUB_PAGES_SUPPLIER_ONLY = {
    "member_directory": ("pages.portal.member_directory", "render"),
}

HUB_PAGES_MEMBER_ONLY = {
    "offers": ("pages.portal.offers", "render"),
    "supplier_portfolio": ("pages.portal.supplier_portfolio", "render"),
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
        pages.update(HUB_PAGES_COMMON)
        session = get_session()
        if session.declarant_type == "member":
            pages.update(HUB_PAGES_MEMBER_ONLY)
        else:
            pages.update(HUB_PAGES_SUPPLIER_ONLY)
        pages.update(PARTNER_MAPPING_PAGES)
    if is_reviewer():
        pages.update(REVIEWER_PAGES)
    if is_admin():
        pages.update(ADMIN_PAGES)

    # Logs page + sidebar item are always available once the user has any app pages.
    if pages:
        pages.update(LOGS_PAGE)

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

    try_process_oauth_callback()

    if show_callback_screen():
        render_connection()
        return

    if not is_authenticated() and not handle_sso_sign_in():
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

    if is_partner():
        remapped = remap_active_page_for_declarant(
            st.session_state.active_page,
            get_session().declarant_type,
        )
        if remapped != st.session_state.active_page:
            st.session_state.active_page = remapped

    if st.session_state.active_page not in pages:
        st.session_state.active_page = default

    if st.session_state.get("navigate_to"):
        target = st.session_state.pop("navigate_to")
        if target in pages:
            st.session_state.active_page = target

    accessible = set(pages.keys())
    handle_sidenav_query(accessible)

    with st.sidebar:
        render_sidenav(st.session_state.active_page, accessible)
        render_dev_controls()

    render_top_header(session.display_name)

    module_path, attr = pages[st.session_state.active_page]
    render_fn = _import_callable(module_path, attr)
    render_page_content(render_fn, st.session_state.active_page)


if __name__ == "__main__":
    main()
