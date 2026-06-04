"""Unit tests for services.memory_store (session fallback, no Snowflake)."""

from __future__ import annotations

from services.memory_store import (
    create_review_entry,
    get_review_entry,
    list_review_entries,
    resolve_template,
    save_global_template,
)


def test_resolve_global_template_after_save(memory_state) -> None:
    columns = ["amount", "partner"]
    review_id = create_review_entry(
        upload_id="UP-1",
        partner_key="MEYLE",
        filename="f.csv",
        period="Q1",
        source_columns=columns,
        status="In review",
        validation_source="NONE",
    )
    save_global_template(
        review_id=review_id,
        mapping={"amount": "EUR_AMOUNT", "partner": "PARTNER_KEY"},
    )

    resolved = resolve_template("MEYLE", columns)
    assert resolved is not None
    assert resolved["scope"] == "GLOBAL"
    assert resolved["mapping"]["amount"] == "EUR_AMOUNT"


def test_resolve_local_template_over_global(memory_state) -> None:
    columns = ["amount", "partner"]
    review_id = create_review_entry(
        upload_id="UP-2",
        partner_key="MEYLE",
        filename="g.csv",
        period="Q1",
        source_columns=columns,
        status="In review",
        validation_source="NONE",
    )
    save_global_template(review_id=review_id, mapping={"amount": "GLOBAL"})
    entry = get_review_entry(review_id)
    assert entry is not None
    sig = entry["source_signature"]
    memory_state.memory_local_templates[f"MEYLE:{sig}"] = {
        "mapping": {"amount": "LOCAL"},
        "source_columns": columns,
    }

    resolved = resolve_template("MEYLE", columns)
    assert resolved is not None
    assert resolved["scope"] == "LOCAL"
    assert resolved["mapping"]["amount"] == "LOCAL"


def test_create_and_list_review_entries(memory_state) -> None:
    create_review_entry(
        upload_id="UP-A",
        partner_key="MEYLE",
        filename="a.csv",
        period="Q1-2026",
        source_columns=["amount"],
        status="In review",
        validation_source="NONE",
    )
    create_review_entry(
        upload_id="UP-B",
        partner_key="HELLA",
        filename="b.csv",
        period="Q1-2026",
        source_columns=["total"],
        status="Validated",
        validation_source="GLOBAL_MEMORY",
        mapping={"total": "EUR_TOTAL"},
    )

    assert len(list_review_entries()) == 2
    filtered = list_review_entries(status_filter="In review", partner_filter="MEYLE")
    assert len(filtered) == 1
    assert filtered[0]["partner_key"] == "MEYLE"


def test_get_review_entry_round_trip(memory_state) -> None:
    review_id = create_review_entry(
        upload_id="UP-Z",
        partner_key="TMD",
        filename="z.csv",
        period="Q2",
        source_columns=["sku", "qty"],
        status="In review",
        validation_source="NONE",
    )
    entry = get_review_entry(review_id)
    assert entry is not None
    assert entry["upload_id"] == "UP-Z"
    assert entry["source_columns"] == ["sku", "qty"]
