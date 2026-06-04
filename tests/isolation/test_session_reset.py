"""Isolation tests — BRD state re-initialization does not duplicate seeded data."""

from __future__ import annotations

import streamlit as st

from services.brd_state import init_brd_state, list_deposits, list_proposals


def test_init_brd_state_is_idempotent(streamlit_session) -> None:
    init_brd_state()
    deposit_count_first = len(st.session_state.deposits)
    proposal_count_first = len(st.session_state.proposals)

    init_brd_state()
    init_brd_state()

    assert len(st.session_state.deposits) == deposit_count_first
    assert len(st.session_state.proposals) == proposal_count_first


def test_fresh_memory_state_has_no_review_entries(memory_state) -> None:
    from services.memory_store import list_review_entries

    assert list_review_entries() == []
