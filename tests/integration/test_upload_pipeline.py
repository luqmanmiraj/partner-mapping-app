"""Integration tests — upload pipeline through memory store and BRD state."""

from __future__ import annotations

import streamlit as st

from services.brd_state import get_deposit
from services.memory_store import list_review_entries, save_global_template
from services.processing_pipeline import process_upload


def test_process_upload_routes_to_review_without_template(
    streamlit_session,
    sample_csv_bytes: bytes,
) -> None:
    streamlit_session.use_snowflake = False
    streamlit_session.passcode = ""

    ok, upload_id, msg = process_upload(
        file_bytes=sample_csv_bytes,
        filename="declaration.csv",
        period="Q1-2026",
        currency="EUR",
        comment="integration test",
        partner_key="MEYLE",
    )
    assert ok is True
    assert upload_id.startswith("DEP-")
    assert "reviewer" in msg.lower() or "review" in msg.lower()

    dep = get_deposit(upload_id)
    assert dep is not None
    assert dep.status == "In review"
    assert dep.line_count == 2

    entries = list_review_entries(partner_filter="MEYLE")
    assert any(e["upload_id"] == upload_id for e in entries)


def test_process_upload_auto_validates_with_global_template(
    streamlit_session,
    sample_csv_bytes: bytes,
) -> None:
    streamlit_session.use_snowflake = False
    streamlit_session.passcode = ""

    columns = ["amount", "partner", "period"]
    review_id = __import__(
        "services.memory_store",
        fromlist=["create_review_entry"],
    ).create_review_entry(
        upload_id="UP-SEED",
        partner_key="MEYLE",
        filename="seed.csv",
        period="Q1",
        source_columns=columns,
        status="In review",
        validation_source="NONE",
    )
    save_global_template(
        review_id=review_id,
        mapping={"amount": "EUR_AMOUNT", "partner": "PARTNER_KEY", "period": "PERIOD"},
    )

    ok, upload_id, msg = process_upload(
        file_bytes=sample_csv_bytes,
        filename="declaration.csv",
        period="Q1-2026",
        currency="EUR",
        comment="",
        partner_key="MEYLE",
    )
    assert ok is True
    assert "validated" in msg.lower() or "memory" in msg.lower()
    assert get_deposit(upload_id).status == "Validated"
