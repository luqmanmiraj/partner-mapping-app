"""Partner — Deposit history screen."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from data.partner_declarations import load_deposit_history
from theme.components import render_data_table, render_page_header, render_section_header


def render(active_page: str = "history") -> None:
    session = get_session()
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    render_page_header(session.display_name, subtitle="Your declaration history")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        history = load_deposit_history(session, conn)

    render_section_header(
        "Deposit History",
        subtitle=f"{len(history)} deposits — sorted by date (newest first)",
    )

    if "history_badge_seen" not in st.session_state:
        pending = len(history[history["Status"].isin(["In review", "Pending processing"])]) if not history.empty else 0
        if pending:
            st.info(f"You have **{pending}** deposit(s) requiring attention.")
        st.session_state.history_badge_seen = True

    render_data_table(history)

    if not history.empty:
        deposit_ids = history["Deposit ID"].tolist()
        selected = st.selectbox("View deposit detail", deposit_ids)
        if st.button("Open detail"):
            st.session_state.selected_deposit_id = selected
            st.session_state.navigate_to = "deposit_detail"
            st.rerun()
