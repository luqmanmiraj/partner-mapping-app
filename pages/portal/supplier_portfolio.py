"""Member Supplier Portfolio portal page (placeholder)."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from theme.components import render_page_header
from theme.html_utils import inject_parent_styles
from theme.member_templates import render_member_template

_MEMBER_SUPPLIER_PORTFOLIO_SCOPE = '[data-testid="stMain"] .st-key-member_supplier_portfolio_page'
_MEMBER_SUPPLIER_PORTFOLIO_STYLE_ID = "member-supplier-portfolio-page"


def _inject_member_supplier_portfolio_page_styles() -> None:
    """Streamlit page CSS — full-width st.html block for supplier portfolio."""
    inject_parent_styles(
        f"""
        {_MEMBER_SUPPLIER_PORTFOLIO_SCOPE} {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}

        {_MEMBER_SUPPLIER_PORTFOLIO_SCOPE} [data-testid="stHtml"],
        {_MEMBER_SUPPLIER_PORTFOLIO_SCOPE} [data-testid="stHtml"] iframe {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        """,
        style_id=_MEMBER_SUPPLIER_PORTFOLIO_STYLE_ID,
    )


def render(active_page: str = "supplier_portfolio") -> None:
    session = get_session()
    render_page_header(session.display_name)
    _inject_member_supplier_portfolio_page_styles()
    with st.container(key="member_supplier_portfolio_page"):
        render_member_template("supplier-portfolio")
