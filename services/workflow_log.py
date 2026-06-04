"""Structured workflow logs (upload → review → save) for supplier dashboard."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import streamlit as st

_LOG_KEY = "nexus_workflow_logs"
_MEMORY_KEY = "memory_workflow_logs"
_MAX_LOGS = 500


@dataclass
class WorkflowLogEntry:
    timestamp: str
    level: str  # success | info | warning | error | issue
    action: str
    actor: str
    upload_id: str = ""
    review_id: str = ""
    partner_key: str = ""
    message: str = ""
    detail: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _init_logs() -> None:
    if _LOG_KEY not in st.session_state:
        backup = st.session_state.get(_MEMORY_KEY, [])
        st.session_state[_LOG_KEY] = list(backup) if backup else []


def _persist_logs(logs: list[dict[str, Any]]) -> None:
    st.session_state[_LOG_KEY] = logs
    st.session_state[_MEMORY_KEY] = logs


def append_log(
    *,
    level: str,
    action: str,
    actor: str,
    message: str,
    upload_id: str = "",
    review_id: str = "",
    partner_key: str = "",
    detail: str = "",
    meta: dict[str, Any] | None = None,
) -> WorkflowLogEntry:
    _init_logs()
    entry = WorkflowLogEntry(
        timestamp=_now(),
        level=level.lower(),
        action=action,
        actor=actor,
        upload_id=upload_id,
        review_id=review_id,
        partner_key=partner_key,
        message=message,
        detail=detail,
        meta=meta or {},
    )
    logs: list[dict[str, Any]] = st.session_state[_LOG_KEY]
    logs.insert(0, entry.to_dict())
    _persist_logs(logs[:_MAX_LOGS])
    return entry


def list_logs(
    *,
    partner_key: str | None = None,
    upload_id: str | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    _init_logs()
    items = list(st.session_state[_LOG_KEY])
    if partner_key:
        items = [i for i in items if i.get("partner_key") == partner_key or not i.get("partner_key")]
    if upload_id:
        items = [i for i in items if i.get("upload_id") == upload_id]
    return items[:limit]


def clear_logs() -> None:
    _persist_logs([])
