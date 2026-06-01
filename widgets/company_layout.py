"""Shared My Company page layout — full-width sections and st.html stretch."""

from __future__ import annotations

from theme.html_utils import render_html
from widgets.company_about_tab import company_about_tab_styles
from widgets.company_contacts_tab import company_contacts_tab_styles
from widgets.company_news_media_tab import company_news_media_tab_styles
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
        "nexus-company-contacts",
        "nexus-company-news",
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
        {_MAIN} .{p}__canvas {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {_MAIN} .stElementContainer:has(.nexus-company-overview),
        {_MAIN} .stElementContainer:has(.nexus-company-tabs),
        {_MAIN} .stElementContainer:has(.nexus-company-about),
        {_MAIN} .stElementContainer:has(.nexus-company-contacts),
        {_MAIN} .stElementContainer:has(.nexus-company-news),
        {_MAIN} .stElementContainer:has(.st-key-company_tabs_nav) {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {_MAIN} .st-key-company_tabs_nav {{
            width: 100% !important;
            max-width: 100% !important;
            margin-bottom: 1.5rem !important;
        }}

        {section_rules}
    """


def inject_company_layout_styles() -> None:
    render_html(f"<style>{company_layout_styles()}</style>")


def inject_all_company_page_styles() -> None:
    """Preload all My Company CSS so tab switches keep styles applied."""
    render_html(
        f"<style>{company_layout_styles()}{company_overview_styles()}"
        f"{company_tabs_styles()}{company_about_tab_styles()}"
        f"{company_contacts_tab_styles()}{company_news_media_tab_styles()}</style>"
    )
