"""Internal — Discrepancy screen."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.qa_loaders import load_discrepancy_matrix
from theme.components import render_data_table, render_page_header, render_section_header


def render(active_page: str = "discrepancy") -> None:
    render_page_header("Reviewer", subtitle="Supplier vs member turnover discrepancies")

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    col1, col2, col3 = st.columns(3)
    with col1:
        period = st.selectbox("Period", ["Q1 2026", "Q4 2025", "All"])
    with col2:
        threshold = st.selectbox("Threshold", ["All", ">1%", ">10%"])
    with col3:
        tag_filter = st.selectbox("Tag", ["All", "Acceptable", "Investigation pending", "Resolved"])

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        matrix = load_discrepancy_matrix(conn)

    if threshold == ">1%":
        matrix = matrix[matrix["Rel. Gap"].str.rstrip("%").astype(float) > 1]
    elif threshold == ">10%":
        matrix = matrix[matrix["Rel. Gap"].str.rstrip("%").astype(float) > 10]
    if tag_filter != "All":
        matrix = matrix[matrix["Tag"] == tag_filter]

    render_section_header("Discrepancy matrix", subtitle=f"{len(matrix)} supplier/member pairs")
    render_data_table(matrix)

    if not matrix.empty:
        pair = st.selectbox("Tag pair", matrix.index.tolist(), format_func=lambda i: matrix.loc[i, "Pair"])
        tag = st.selectbox("Apply tag", ["Acceptable", "Investigation pending", "Resolved"])
        if st.button("Save tag"):
            from services.review_service import save_qa_tag

            pair_label = str(matrix.loc[pair, "Pair"])
            save_qa_tag(pair_label, "discrepancy", tag, tag, actor="reviewer")
            st.success(f"Tagged {pair_label} as {tag}")
