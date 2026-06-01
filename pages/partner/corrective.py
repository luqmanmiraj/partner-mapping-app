"""Partner — Corrective deposit screen."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from data.partner_declarations import check_period_closed
from services.upload_client import upload_declaration
from theme.components import render_page_header, render_section_header, render_warning_banner
from constants import upload_size_help
from theme.tokens import CURRENCIES


def render(active_page: str = "corrective") -> None:
    session = get_session()
    render_page_header(session.display_name, subtitle="Submit a correction for a previous period")

    render_section_header(
        "Corrective Deposit",
        subtitle="Previous deposit will be marked Superseded — both preserved in history",
    )

    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "Period to correct",
            ["April 2026", "March 2026", "Q1 2026", "Q4 2025", "December 2025"],
        )
    with col2:
        original_id = st.text_input("Original deposit ID (optional)", placeholder="DEP-2026-0042")

    if check_period_closed(session.partner_key, period):
        render_warning_banner(
            f"Period **{period}** is closed. Your correction will not modify the accounting snapshot "
            "— it will generate an alert for the admin to evaluate."
        )

    currency = st.selectbox("Currency", CURRENCIES, index=CURRENCIES.index(session.default_currency) if session.default_currency in CURRENCIES else 0)
    uploaded = st.file_uploader(
        "Corrected file",
        type=["csv", "xlsx", "xls"],
        help=upload_size_help(),
    )
    comment = st.text_area("Reason for correction", max_chars=500)

    if st.button("Submit corrective deposit", type="primary"):
        if uploaded is None:
            st.error("Please attach the corrected file.")
        else:
            result = upload_declaration(
                file_bytes=uploaded.getvalue(),
                filename=uploaded.name,
                period=period,
                currency=currency,
                comment=f"[CORRECTIVE {original_id}] {comment}",
                partner_key=session.partner_key,
                is_corrective=True,
                supersedes_upload_id=original_id or "",
            )
            if result.success:
                st.success(
                    f"Corrective deposit submitted ({result.upload_id}). "
                    f"Previous deposit will be marked Superseded when processing completes."
                )
            else:
                st.error(result.error)
