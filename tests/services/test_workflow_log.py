"""Unit tests for workflow log and upload workflow tracking."""

from __future__ import annotations

from services.upload_workflow import (
    compute_mapping_diff,
    detect_mapping_issues,
    save_workflow,
    UploadWorkflow,
)
from services.workflow_log import append_log, list_logs


def test_append_and_list_logs(streamlit_session) -> None:
    append_log(
        level="info",
        action="TEST",
        actor="pytest",
        partner_key="MEYLE",
        message="hello",
    )
    logs = list_logs(partner_key="MEYLE")
    assert logs[0]["message"] == "hello"


def test_compute_mapping_diff() -> None:
    before = {"A": "ignore", "B": "amount"}
    after = {"A": "partner_name", "B": "amount", "C": "ignore"}
    diff = compute_mapping_diff(before, after)
    assert ("A", "ignore", "partner_name") in diff


def test_detect_mapping_issues_duplicate_targets() -> None:
    issues = detect_mapping_issues(
        ["Col1", "Col2"],
        {"Col1": "amount", "Col2": "amount"},
    )
    assert any("multiple" in i.lower() for i in issues)


def test_save_workflow_round_trip(streamlit_session) -> None:
    save_workflow(
        UploadWorkflow(
            upload_id="DEP-T",
            review_id="REV-T",
            partner_key="MEYLE",
            filename="t.csv",
            period="Q1",
            currency="EUR",
            status="In review",
            validation_source="NONE",
            source_columns=["a"],
        )
    )
    from services.upload_workflow import get_workflow

    wf = get_workflow("DEP-T")
    assert wf is not None
    assert wf["review_id"] == "REV-T"
