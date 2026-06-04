"""Isolation tests — partner-scoped data must not leak across partners."""

from __future__ import annotations

from services.brd_state import get_deposit, list_deposits, save_deposit, DepositRecord
from services.memory_store import create_review_entry, list_review_entries
from services.processing_pipeline import process_upload


def test_deposits_isolated_by_partner(streamlit_session, sample_csv_bytes: bytes) -> None:
    streamlit_session.use_snowflake = False
    streamlit_session.passcode = ""

    ok_m, dep_m, _ = process_upload(
        file_bytes=sample_csv_bytes,
        filename="meyle.csv",
        period="Q1-2026",
        currency="EUR",
        comment="",
        partner_key="MEYLE",
    )
    ok_h, dep_h, _ = process_upload(
        file_bytes=sample_csv_bytes,
        filename="hella.csv",
        period="Q1-2026",
        currency="EUR",
        comment="",
        partner_key="HELLA",
    )
    assert ok_m and ok_h

    meyle_ids = {d.upload_id for d in list_deposits("MEYLE")}
    hella_ids = {d.upload_id for d in list_deposits("HELLA")}

    assert dep_m in meyle_ids
    assert dep_m not in hella_ids
    assert dep_h in hella_ids
    assert dep_h not in meyle_ids


def test_review_queue_isolated_by_partner(memory_state, streamlit_session) -> None:
    create_review_entry(
        upload_id="UP-MEYLE",
        partner_key="MEYLE",
        filename="a.csv",
        period="Q1",
        source_columns=["amount"],
        status="In review",
        validation_source="NONE",
    )
    create_review_entry(
        upload_id="UP-HELLA",
        partner_key="HELLA",
        filename="b.csv",
        period="Q1",
        source_columns=["total"],
        status="In review",
        validation_source="NONE",
    )

    meyle = list_review_entries(partner_filter="MEYLE")
    hella = list_review_entries(partner_filter="HELLA")

    assert all(e["partner_key"] == "MEYLE" for e in meyle)
    assert all(e["partner_key"] == "HELLA" for e in hella)
    assert not any(e["upload_id"] == "UP-HELLA" for e in meyle)
    assert not any(e["upload_id"] == "UP-MEYLE" for e in hella)


def test_manual_deposit_save_does_not_cross_partners(brd_state) -> None:
    save_deposit(
        DepositRecord(
            upload_id="DEP-ISO-A",
            partner_key="TMD",
            period="Q4-2025",
            currency="EUR",
            filename="tmd.csv",
            comment="",
        )
    )
    assert get_deposit("DEP-ISO-A") is not None
    assert "DEP-ISO-A" not in {d.upload_id for d in list_deposits("MEYLE")}
