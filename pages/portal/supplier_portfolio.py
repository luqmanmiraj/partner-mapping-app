"""Member Supplier Portfolio — REF.SUPPLIER + BRAND."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from data.portal_loaders import load_supplier_portfolio
from theme.components import render_page_header, render_data_table
from theme.html_utils import inject_parent_styles
from theme.member_templates import render_member_template

_MEMBER_SUPPLIER_PORTFOLIO_SCOPE = '[data-testid="stMain"] .st-key-member_supplier_portfolio_page'
_MEMBER_SUPPLIER_PORTFOLIO_STYLE_ID = "member-supplier-portfolio-page"


def _inject_member_supplier_portfolio_page_styles() -> None:
    inject_parent_styles(
        f"""
        {_MEMBER_SUPPLIER_PORTFOLIO_SCOPE} {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}
        """,
        style_id=_MEMBER_SUPPLIER_PORTFOLIO_STYLE_ID,
    )


def render(active_page: str = "supplier_portfolio") -> None:
    session = get_session()
    render_page_header(session.display_name)
    _inject_member_supplier_portfolio_page_styles()

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            df = load_supplier_portfolio(conn)
            if not df.empty:
                st.subheader("Supplier portfolio (REF.SUPPLIER)")
                render_data_table(df)
                return

    with st.container(key="member_supplier_portfolio_page"):
        render_member_template("supplier-portfolio")
