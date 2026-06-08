"""Internal — Overlap investigation."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.qa_loaders import load_overlap_cases
from theme.components import render_data_table, render_page_header, render_section_header


def render(active_page: str = "overlap") -> None:
    render_page_header("Reviewer", subtitle="Parent vs descendant declaration overlaps")

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        cases = load_overlap_cases(conn)

    render_section_header("Overlap cases", subtitle="From QA.V_DOUBLE_COUNTING_CHECK")
    render_data_table(cases)

    if not cases.empty:
        case_id = st.selectbox("Investigate case", cases["Case ID"].tolist())
        action = st.radio(
            "Resolution",
            ["Parent wins", "Descendants win", "Manual investigation needed"],
            horizontal=True,
        )
        if st.button("Save resolution"):
            from services.review_service import save_qa_tag

            save_qa_tag(case_id, "overlap", action, action, actor="reviewer")
            st.success(f"Case {case_id}: {action}")
