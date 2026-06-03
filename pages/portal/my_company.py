"""My Company portal page — overview and tabbed company profile sections."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from data.my_company_fixtures import (
    ABOUT_TAB,
    CONTACTS,
    DOCUMENTS,
    GALLERY_ITEMS,
    MEDIA_ITEMS,
    NEWS_FEATURED,
    NEWS_SIDEBAR,
    OVERVIEW,
)
from theme.components import render_page_header
from theme.html_utils import inject_parent_styles
from theme.member_templates import render_member_company_tabs
from widgets.company_layout import inject_all_company_page_styles
from widgets.company_overview import render_company_overview
from widgets.company_tabs import render_company_tabs

_MEMBER_COMPANY_SCOPE = '[data-testid="stMain"] .st-key-member_company_page'
_MEMBER_COMPANY_STYLE_ID = "member-company-page"
_SUPPLIER_COMPANY_SCOPE = '[data-testid="stMain"] .st-key-supplier_company_page'
_SUPPLIER_COMPANY_STYLE_ID = "supplier-company-page"


def _inject_member_company_page_styles() -> None:
    """Streamlit page CSS — full-width st.html block for member My Company."""
    inject_parent_styles(
        f"""
        {_MEMBER_COMPANY_SCOPE} {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}

        {_MEMBER_COMPANY_SCOPE} [data-testid="stHtml"],
        {_MEMBER_COMPANY_SCOPE} [data-testid="stHtml"] iframe {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        """,
        style_id=_MEMBER_COMPANY_STYLE_ID,
    )


def _inject_supplier_company_page_styles() -> None:
    """Streamlit page CSS — full-width st.html blocks for supplier My Company."""
    inject_parent_styles(
        f"""
        {_SUPPLIER_COMPANY_SCOPE} {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}

        {_SUPPLIER_COMPANY_SCOPE} [data-testid="stHtml"],
        {_SUPPLIER_COMPANY_SCOPE} [data-testid="stHtml"] iframe {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        """,
        style_id=_SUPPLIER_COMPANY_STYLE_ID,
    )


def render(active_page: str = "my_company") -> None:
    session = get_session()
    # For member persona, render the static company profile HTML prototype.
    if getattr(session, "declarant_type", "") == "member":
        render_page_header(session.display_name)
        _inject_member_company_page_styles()
        with st.container(key="member_company_page"):
            render_member_company_tabs()
        return

    render_page_header(session.display_name)
    _inject_supplier_company_page_styles()
    inject_all_company_page_styles()

    with st.container(key="supplier_company_page"):
        render_company_overview(OVERVIEW)

        news_data = {
            "featured": NEWS_FEATURED,
            "sidebar": NEWS_SIDEBAR,
            "documents": DOCUMENTS,
            "videos": MEDIA_ITEMS,
            "gallery": GALLERY_ITEMS,
        }
        render_company_tabs(ABOUT_TAB, CONTACTS, news_data)

    _inject_supplier_company_page_styles()
    inject_all_company_page_styles()
