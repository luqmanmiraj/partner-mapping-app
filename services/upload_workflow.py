"""Session-scoped upload → review → save workflow state."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import streamlit as st

_WORKFLOWS_KEY = "nexus_upload_workflows"


@dataclass
class MappingChange:
    source_column: str
    from_target: str
    to_target: str
    changed_by: str
    changed_at: str


@dataclass
class UploadWorkflow:
    upload_id: str
    review_id: str
    partner_key: str
    filename: str
    period: str
    currency: str
    status: str
    validation_source: str
    source_columns: list[str]
    sheet_name: str = ""
    row_count: int = 0
    truncated: bool = False
    mapping_at_upload: dict[str, str] = field(default_factory=dict)
    mapping_at_review_open: dict[str, str] = field(default_factory=dict)
    mapping_final: dict[str, str] = field(default_factory=dict)
    mapping_changes: list[MappingChange] = field(default_factory=list)
    reviewer_note: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["mapping_changes"] = [asdict(c) for c in self.mapping_changes]
        return data


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _init() -> None:
    if _WORKFLOWS_KEY not in st.session_state:
        st.session_state[_WORKFLOWS_KEY] = {}


def save_workflow(workflow: UploadWorkflow) -> None:
    _init()
    workflow.updated_at = _now()
    if not workflow.created_at:
        workflow.created_at = workflow.updated_at
    st.session_state[_WORKFLOWS_KEY][workflow.upload_id] = workflow.to_dict()


def get_workflow(upload_id: str) -> dict[str, Any] | None:
    _init()
    return st.session_state[_WORKFLOWS_KEY].get(upload_id)


def get_workflow_by_review(review_id: str) -> dict[str, Any] | None:
    _init()
    for wf in st.session_state[_WORKFLOWS_KEY].values():
        if wf.get("review_id") == review_id:
            return wf
    return None


def list_workflows(*, partner_key: str | None = None) -> list[dict[str, Any]]:
    _init()
    items = list(st.session_state[_WORKFLOWS_KEY].values())
    if partner_key:
        items = [w for w in items if w.get("partner_key") == partner_key]
    return sorted(items, key=lambda w: w.get("updated_at", ""), reverse=True)


def record_mapping_snapshot(review_id: str, mapping: dict[str, str], *, phase: str) -> None:
    """phase: review_open | final"""
    wf = get_workflow_by_review(review_id)
    if not wf:
        return
    upload_id = wf["upload_id"]
    if phase == "review_open":
        wf["mapping_at_review_open"] = dict(mapping)
    elif phase == "final":
        wf["mapping_final"] = dict(mapping)
    wf["updated_at"] = _now()
    st.session_state[_WORKFLOWS_KEY][upload_id] = wf


def append_mapping_changes(
    review_id: str,
    changes: list[MappingChange],
    *,
    reviewer_note: str = "",
) -> None:
    wf = get_workflow_by_review(review_id)
    if not wf:
        return
    upload_id = wf["upload_id"]
    existing = [MappingChange(**c) for c in wf.get("mapping_changes", [])]
    existing.extend(changes)
    wf["mapping_changes"] = [asdict(c) for c in existing]
    if reviewer_note:
        wf["reviewer_note"] = reviewer_note
    wf["updated_at"] = _now()
    st.session_state[_WORKFLOWS_KEY][upload_id] = wf


def compute_mapping_diff(
    before: dict[str, str],
    after: dict[str, str],
) -> list[tuple[str, str, str]]:
    """Return list of (source, from_target, to_target) for real changes only."""
    diff: list[tuple[str, str, str]] = []
    all_sources = set(before) | set(after)
    for source in sorted(all_sources):
        old = before.get(source, "ignore")
        new = after.get(source, "ignore")
        if old != new:
            diff.append((source, old, new))
    return diff


def detect_mapping_issues(
    source_columns: list[str],
    mapping: dict[str, str],
) -> list[str]:
    """Return human-readable issues for suspicious column mapping."""
    issues: list[str] = []
    targets_used: dict[str, list[str]] = {}

    for col in source_columns:
        name = str(col).strip()
        if not name or name.lower().startswith("unnamed"):
            issues.append(f"Source column '{col}' is not a valid header — mapping may be wrong.")
        target = mapping.get(col, mapping.get(name, "ignore"))
        if target and target != "ignore":
            targets_used.setdefault(target, []).append(name or col)

    for target, sources in targets_used.items():
        if len(sources) > 1:
            issues.append(
                f"Target field '{target}' is mapped from multiple sources: {', '.join(sources)}."
            )

    mapped_count = sum(1 for t in mapping.values() if t and t != "ignore")
    if source_columns and mapped_count == 0:
        issues.append("No columns mapped to target fields (all set to ignore).")

    return issues
