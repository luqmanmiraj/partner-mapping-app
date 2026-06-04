"""Unit tests for services.closure_service."""

from __future__ import annotations

import streamlit as st

from services.brd_state import DepositRecord, save_deposit
from services.closure_service import close_quarter, record_post_billing_mod


def test_close_quarter_blocked_when_deposit_in_review(brd_state) -> None:
    save_deposit(
        DepositRecord(
            upload_id="DEP-BLOCK",
            partner_key="MEYLE",
            period="Q1-2026",
            currency="EUR",
            filename="x.csv",
            comment="",
            status="In review",
        )
    )
    ok, msg = close_quarter("MEYLE", "Q1-2026")
    assert ok is False
    assert "In review" in msg


def test_close_quarter_success(brd_state) -> None:
    save_deposit(
        DepositRecord(
            upload_id="DEP-OK",
            partner_key="MEYLE",
            period="Q2-2026",
            currency="EUR",
            filename="ok.csv",
            comment="",
            status="Validated",
        )
    )
    ok, msg = close_quarter("MEYLE", "Q2-2026")
    assert ok is True
    assert "SNAP-" in msg
    assert ("MEYLE", "Q2-2026") in st.session_state.closed_periods


def test_record_post_billing_mod(brd_state) -> None:
    record_post_billing_mod("MEYLE", "Q1-2025", "Correction after invoice", actor="admin")
    assert len(st.session_state.post_billing_mods) == 1
    assert st.session_state.post_billing_mods[0]["reason"] == "Correction after invoice"
