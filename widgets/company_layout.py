"""Shared My Company page layout — full-width sections and st.html stretch."""

from __future__ import annotations

from theme.html_utils import render_html
from widgets.company_about_tab import company_about_tab_styles
from widgets.company_overview import company_overview_styles
from widgets.company_tabs import company_tabs_styles

_PREFIX = "nexus-company-layout"
_MAIN = '[data-testid="stMain"]'


def company_layout_styles() -> str:
    p = _PREFIX
    sections = (
        "nexus-company-overview",
        "nexus-company-tabs",
        "nexus-company-about",
    )
    section_rules = "\n".join(
        f"""
        {_MAIN} .{name} {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box;
        }}"""
        for name in sections
    )
    return f"""
        {_MAIN} [data-testid="stHtml"]:has(.nexus-company-about),
        {_MAIN} [data-testid="stHtml"]:has(.cmpc-page-wrapper),
        {_MAIN} [data-testid="stHtml"]:has(.cmpn-page-wrapper) {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {_MAIN} .st-key-company_about_tab_container,
        {_MAIN} .st-key-company_contacts_tab_container,
        {_MAIN} .st-key-company_news_tab_container,
        {_MAIN} .st-key-company_tabs_nav {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {_MAIN} .st-key-company_tabs_nav {{
            margin-bottom: 1.5rem !important;
        }}

        {_MAIN} .stElementContainer:has(.nexus-company-overview),
        {_MAIN} .stElementContainer:has(.st-key-company_tabs_nav),
        {_MAIN} .stElementContainer:has(.st-key-company_about_tab_container),
        {_MAIN} .stElementContainer:has(.st-key-company_contacts_tab_container),
        {_MAIN} .stElementContainer:has(.st-key-company_news_tab_container) {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {_MAIN} .{p}__canvas {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {section_rules}
    """


def inject_company_layout_styles() -> None:
    render_html(f"<style>{company_layout_styles()}</style>")


def inject_all_company_page_styles() -> None:
    """Preload layout, overview, tabs, about (contacts/news CSS lives in st.html)."""
    render_html(
        f"<style>{company_layout_styles()}{company_overview_styles()}"
        f"{company_tabs_styles()}{company_about_tab_styles()}</style>"
    )
