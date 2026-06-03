"""Internal — Bulk review screen."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.review_queue import load_review_queue
from services.review_service import bulk_action
from theme.components import render_page_header, render_section_header


def render(active_page: str = "bulk_review") -> None:
    render_page_header("Reviewer", subtitle="Process repetitive mapping cases in batch")

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        queue = load_review_queue(conn)

    render_section_header("Select proposals for bulk action")

    if queue.empty:
        st.info("No proposals in queue.")
        return

    selected = st.multiselect("Proposals", queue["Proposal ID"].tolist())
    action = st.selectbox("Action", ["Validate all as-is", "Reject all"])

    if st.button("Apply bulk action", type="primary") and selected:
        st.success(bulk_action(selected, action))
