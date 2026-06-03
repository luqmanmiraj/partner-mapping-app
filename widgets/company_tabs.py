"""My Company tab navigation — About / Contacts / News & Media."""

from __future__ import annotations

import streamlit as st

from theme.html_utils import render_st_html_page
from widgets.company_about_tab import (
    build_company_about_tab_html,
    company_about_tab_styles,
)
from widgets.company_contacts_tab import render_company_contacts_tab
from widgets.company_news_media_tab import render_company_news_media_tab

_PREFIX = "nexus-company-tabs"
_SESSION_KEY = "nexus_company_active_tab"
_NAV_KEY = "company_tabs_nav"
_MAIN = '[data-testid="stMain"]'

TAB_ABOUT = "about"
TAB_CONTACTS = "contacts"
TAB_NEWS = "news_media"

_TABS: tuple[tuple[str, str, str], ...] = (
    (TAB_ABOUT, "About", "company_tab_about"),
    (TAB_CONTACTS, "Contacts", "company_tab_contacts"),
    (TAB_NEWS, "News & Media", "company_tab_news"),
)


def _active_tab() -> str:
    active = st.session_state.get(_SESSION_KEY, TAB_ABOUT)
    if active not in {t[0] for t in _TABS}:
        active = TAB_ABOUT
    return active


def company_tabs_styles() -> str:
    p = _PREFIX
    nav = f"{_MAIN} .st-key-{_NAV_KEY}"
    return f"""
        {nav} {{
            width: 100% !important;
            max-width: 100% !important;
            margin: 0 0 1.5rem 0 !important;
            padding: 0 !important;
            border-bottom: 2px solid #e2e8f0 !important;
            align-items: flex-end !important;
            flex-wrap: nowrap !important;
            gap: 25px !important;
        }}

        {nav} [data-testid="stButton"] {{
            margin: 0 !important;
            flex: 0 0 auto !important;
            width: auto !important;
        }}

        {nav} [data-testid="stButton"] > button {{
            width: auto !important;
            min-height: 40px !important;
            padding: 0 2px 10px 2px !important;
            margin: 0 !important;
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            color: #718096 !important;
            border-bottom: 3px solid transparent !important;
            white-space: nowrap !important;
            cursor: pointer !important;
        }}

        {nav} [data-testid="stButton"] > button:hover {{
            color: #1a1a1a !important;
            background: transparent !important;
        }}

        {nav} [data-testid="stButton"] > button[kind="secondary"],
        {nav} [data-testid="stButton"] > button[data-testid="stBaseButton-secondary"] {{
            color: #718096 !important;
            background: transparent !important;
            border-bottom-color: transparent !important;
        }}

        {nav} [data-testid="stButton"] > button[kind="primary"],
        {nav} [data-testid="stButton"] > button[data-testid="stBaseButton-primary"] {{
            color: #1a1a1a !important;
            background: transparent !important;
            border: none !important;
            border-bottom: 3px solid #f39c12 !important;
            box-shadow: none !important;
        }}
    """


def inject_company_tabs_styles() -> None:
    from theme.html_utils import render_html

    render_html(f"<style>{company_tabs_styles()}</style>")


def render_company_tabs(
    about_data: dict,
    contacts: list[dict[str, str]],
    news_data: dict,
) -> None:
    inject_company_tabs_styles()
    active = _active_tab()

    with st.container(horizontal=True, key=_NAV_KEY, gap="small"):
        for tab_id, label, btn_key in _TABS:
            is_active = active == tab_id
            if st.button(
                label,
                key=btn_key,
                type="primary" if is_active else "secondary",
            ):
                if not is_active:
                    st.session_state[_SESSION_KEY] = tab_id
                    st.rerun()

    if active == TAB_ABOUT:
        with st.container(key="company_about_tab_container"):
            render_st_html_page(
                company_about_tab_styles(),
                build_company_about_tab_html(about_data),
                width="stretch",
            )
    elif active == TAB_CONTACTS:
        with st.container(key="company_contacts_tab_container"):
            render_company_contacts_tab(contacts)
    else:
        with st.container(key="company_news_tab_container"):
            render_company_news_media_tab(news_data)
