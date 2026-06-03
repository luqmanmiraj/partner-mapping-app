"""Partner — Deposit detail screen."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from data.partner_declarations import load_deposit_detail
from theme.components import (
    render_metric_cards,
    render_page_header,
    render_section_header,
    status_badge_html,
)
from theme.html_utils import render_html


def render(active_page: str = "deposit_detail") -> None:
    session = get_session()
    deposit_id = st.session_state.get("selected_deposit_id", "DEP-2026-0042")
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    render_page_header(session.display_name, subtitle="Deposit detail")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        detail = load_deposit_detail(deposit_id, session, conn)
    csv_data = detail.get("reconciled_csv", "line,amount,status\n")

    render_html(
        f"""
        <div class="card">
            <strong>{deposit_id}</strong> — {detail["period"]}
            &nbsp; {status_badge_html(detail["status"])}
        </div>
        """
    )

    render_section_header("Line breakdown", subtitle=f"Submitted: {detail['submitted_at']}")

    render_metric_cards(
        [
            {"label": "Auto-validated", "value": f"{detail['auto_validated']:,}", "delta": "≥90% confidence", "positive": True},
            {"label": "In review", "value": f"{detail['in_review']:,}", "delta": "Awaiting reviewer", "positive": False},
            {"label": "Rejected", "value": f"{detail['rejected']:,}", "delta": "With reasons", "positive": False},
            {
                "label": f"Total ({detail['currency']})",
                "value": f"{detail['local_total']:,.0f}",
                "delta": f"€{detail['eur_total']:,.0f} EUR",
                "positive": True,
            },
        ]
    )

    if detail.get("rejection_reasons"):
        render_section_header("Rejection reasons")
        for reason in detail["rejection_reasons"]:
            st.markdown(f"- {reason}")

    st.download_button(
        "Download reconciled file",
        data=csv_data,
        file_name=f"{deposit_id}_reconciled.csv",
        mime="text/csv",
    )
