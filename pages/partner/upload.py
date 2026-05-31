"""Partner — Declaration upload screen."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from services.upload_client import upload_declaration
from theme.components import render_page_header, render_section_header, render_warning_banner
from constants import MAX_UPLOAD_BYTES, MAX_UPLOAD_MB, upload_size_error, upload_size_help
from theme.tokens import CURRENCIES


def render(active_page: str = "upload") -> None:
    session = get_session()
    render_page_header(session.display_name, subtitle="Submit a new declaration")

    render_section_header(
        "Declaration Upload",
        subtitle=f"Upload your turnover data — counterparty dimension: {session.counterparty_label}",
    )

    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "Period",
            ["April 2026", "March 2026", "Q1 2026", "February 2026", "January 2026"],
        )
    with col2:
        currency = st.selectbox(
            "Currency",
            CURRENCIES,
            index=CURRENCIES.index(session.default_currency) if session.default_currency in CURRENCIES else 0,
        )

    uploaded = st.file_uploader(
        "Drag & drop your file here",
        type=["csv", "xlsx", "xls"],
        help=upload_size_help(),
        max_upload_size=MAX_UPLOAD_MB,
    )

    comment = st.text_area("Comment (optional)", max_chars=500, placeholder="Max 500 characters")

    if st.button("Submit declaration", type="primary"):
        if uploaded is None:
            st.error("Please select a file before submitting.")
        elif len(uploaded.getvalue()) > MAX_UPLOAD_BYTES:
            st.error(upload_size_error())
        else:
            result = upload_declaration(
                file_bytes=uploaded.getvalue(),
                filename=uploaded.name,
                period=period,
                currency=currency,
                comment=comment,
                partner_key=session.partner_key,
            )
            if result.success:
                st.success(result.message)
                st.info(f"Deposit ID: **{result.upload_id}** — you can track progress in Deposit History.")
            else:
                st.error(result.error)

    st.markdown("---")
    st.caption(
        "BRD: Period selector, currency (pre-filled with partner default), "
        "drag & drop upload, optional comment, submit. Processing continues in background."
    )
