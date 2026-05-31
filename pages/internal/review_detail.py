"""Internal — Granular review screen."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.review_queue import load_review_detail
from services.review_service import reject_proposal, validate_proposal
from theme.components import render_page_header, render_section_header


def render(active_page: str = "review_detail") -> None:
    render_page_header("Reviewer", subtitle="Granular mapping review")

    proposal_id = st.session_state.get("selected_proposal_id", "MAP-8842")
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        detail = load_review_detail(proposal_id, conn)

    st.write(f"**{detail['proposal_id']}** — {detail['partner']} / {detail['dimension']} — confidence {detail['confidence']:.0%}")

    col1, col2 = st.columns(2)
    with col1:
        st.text_area("Source value", value=detail["source_value"], disabled=True)
    with col2:
        modified = st.text_input("Proposed target", value=detail["proposed_target"])

    memory_scope = st.radio("Memory scope (BR-MAP-04 LOCAL priority)", ["LOCAL", "GLOBAL"], horizontal=True)
    comment = st.text_area("Comment", max_chars=1000)
    tags = st.multiselect("Tags", ["Recurring case", "Partner training needed", "Edge case"])

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Validate as-is", type="primary"):
            st.success(validate_proposal(proposal_id, memory_scope=memory_scope, comment=comment, tags=tags))
    with c2:
        if st.button("Modify & validate"):
            st.success(
                validate_proposal(
                    proposal_id,
                    modified_target=modified,
                    memory_scope=memory_scope,
                    comment=comment,
                    tags=tags,
                )
            )
    with c3:
        reason = st.text_input("Rejection reason")
        if st.button("Reject"):
            st.warning(reject_proposal(proposal_id, reason))
