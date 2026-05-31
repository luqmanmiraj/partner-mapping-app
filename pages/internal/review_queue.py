"""Internal — Review queue."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.review_queue import load_review_queue
from theme.components import render_data_table, render_page_header, render_section_header


def render(active_page: str = "review_queue") -> None:
    render_page_header("Reviewer", subtitle="Mapping proposals below confidence threshold")

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    col1, col2, col3 = st.columns(3)
    with col1:
        partner = st.selectbox("Partner", ["All", "MEYLE", "HELLA", "TMD", "MEMBER_DE_001"])
    with col2:
        dimension = st.selectbox(
            "Dimension",
            ["All", "product_category", "counterparty_member", "counterparty_supplier"],
        )
    with col3:
        max_conf = st.slider("Max confidence", 0.0, 0.9, 0.9, 0.05)

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        queue = load_review_queue(
            conn,
            partner_filter=partner,
            dimension_filter=dimension,
            max_confidence=max_conf,
        )

    render_section_header("Review Queue", subtitle=f"{len(queue)} proposals pending")
    render_data_table(queue)

    if not queue.empty:
        pid = st.selectbox("Open proposal", queue["Proposal ID"].tolist())
        if st.button("Review"):
            st.session_state.selected_proposal_id = pid
            st.session_state.navigate_to = "review_detail"
            st.rerun()
