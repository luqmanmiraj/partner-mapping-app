"""BRD pipeline step logging — Steps 1–7 trace for admin monitoring."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import streamlit as st

# BRD pipeline steps (Business_Requirements / DEVELOPER_GUIDE §3.3)
BRD_PIPELINE_STEPS: list[tuple[int, str, str]] = [
    (1, "Parsing", "Read file, detect encoding/separator, extract lines"),
    (2, "Form Mapping", "Apply partner column template → canonical columns"),
    (3, "Auto-correction", "Trivial anomaly fixes; reject or suggest reprocess"),
    (4, "Value Mapping", "LOCAL → GLOBAL → Cortex for 3 dimensions per line"),
    (5, "Auto-validation", "Confidence ≥ threshold → VALIDATED_LINE else review queue"),
    (6, "Currency Conversion", "Provisional EUR via ECB rate; pending_final_rate flag"),
    (7, "Notification", "Partner notification + cockpit badge"),
]


@dataclass
class PipelineLogEntry:
    log_id: str
    upload_id: str
    partner_key: str
    step_number: int
    step_name: str
    status: str
    detail: str
    snowflake_target: str = ""
    created_at: str = ""


class PipelineLogger:
    """Accumulates step logs for one upload run."""

    def __init__(self, *, upload_id: str, partner_key: str, conn=None) -> None:
        self.upload_id = upload_id
        self.partner_key = partner_key
        self.conn = conn
        self._entries: list[PipelineLogEntry] = []

    def log(
        self,
        step_number: int,
        step_name: str,
        status: str,
        detail: str,
        *,
        snowflake_target: str = "",
    ) -> None:
        entry = PipelineLogEntry(
            log_id=f"LOG-{uuid.uuid4().hex[:10].upper()}",
            upload_id=self.upload_id,
            partner_key=self.partner_key,
            step_number=step_number,
            step_name=step_name,
            status=status,
            detail=detail,
            snowflake_target=snowflake_target,
            created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        )
        self._entries.append(entry)
        _persist_entry(entry, self.conn)
        audit_pipeline(entry)

    @property
    def entries(self) -> list[PipelineLogEntry]:
        return list(self._entries)


def _init_session_logs() -> None:
    if "pipeline_logs" not in st.session_state:
        st.session_state.pipeline_logs: dict[str, list[dict]] = {}


def _persist_entry(entry: PipelineLogEntry, conn) -> None:
    _init_session_logs()
    bucket = st.session_state.pipeline_logs.setdefault(entry.upload_id, [])
    bucket.append(
        {
            "log_id": entry.log_id,
            "upload_id": entry.upload_id,
            "partner_key": entry.partner_key,
            "step_number": entry.step_number,
            "step_name": entry.step_name,
            "status": entry.status,
            "detail": entry.detail,
            "snowflake_target": entry.snowflake_target,
            "created_at": entry.created_at,
        }
    )

    if conn is None:
        return

    from auth.snowflake_session import schema_fqn

    table = f"{schema_fqn('APP')}.PIPELINE_LOG"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (
                log_id, upload_id, partner_key, step_number, step_name,
                status, detail, snowflake_target, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP())
            """,
            (
                entry.log_id,
                entry.upload_id,
                entry.partner_key,
                entry.step_number,
                entry.step_name,
                entry.status,
                entry.detail[:4000],
                entry.snowflake_target or None,
            ),
        )
    except Exception as exc:
        bucket[-1]["snowflake_persist_error"] = str(exc)
    finally:
        cur.close()


def audit_pipeline(entry: PipelineLogEntry) -> None:
    from services.brd_state import audit

    audit(
        entry.partner_key,
        f"PIPELINE_STEP_{entry.step_number}",
        f"[{entry.status}] {entry.step_name}: {entry.detail}",
    )


def list_pipeline_logs(
    upload_id: str,
    *,
    conn=None,
) -> list[dict[str, Any]]:
    _init_session_logs()
    session_rows = st.session_state.pipeline_logs.get(upload_id, [])

    if conn is not None:
        from auth.snowflake_session import schema_fqn
        from snowflake_client import query_df

        safe_id = upload_id.replace("'", "''")
        try:
            df = query_df(
                conn,
                f"""
                SELECT log_id, upload_id, partner_key, step_number, step_name,
                       status, detail, snowflake_target,
                       TO_VARCHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
                FROM {schema_fqn('APP')}.PIPELINE_LOG
                WHERE upload_id = '{safe_id}'
                ORDER BY step_number, created_at
                """,
            )
            if not df.empty:
                return df.to_dict(orient="records")
        except Exception:
            pass

    return sorted(session_rows, key=lambda r: (r.get("step_number", 0), r.get("created_at", "")))


def list_recent_uploads(
    *,
    partner_filter: str = "All",
    conn=None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    _init_session_logs()

    if conn is not None:
        from auth.snowflake_session import schema_fqn
        from snowflake_client import query_df

        clause = ""
        if partner_filter != "All":
            safe = partner_filter.replace("'", "''")
            clause = f"WHERE partner_key = '{safe}'"
        try:
            df = query_df(
                conn,
                f"""
                SELECT upload_id, partner_key, filename, period_label, status,
                       line_count, auto_validated_count, in_review_count,
                       TO_VARCHAR(submitted_at, 'YYYY-MM-DD HH24:MI') AS submitted_at
                FROM {schema_fqn('STAGING')}.RAW_FILE
                {clause}
                ORDER BY submitted_at DESC
                LIMIT {int(limit)}
                """,
            )
            if not df.empty:
                return df.to_dict(orient="records")
        except Exception:
            pass

    from services.brd_state import init_brd_state

    init_brd_state()
    rows = []
    for dep in st.session_state.deposits.values():
        if partner_filter != "All" and dep.partner_key != partner_filter:
            continue
        rows.append(
            {
                "UPLOAD_ID": dep.upload_id,
                "PARTNER_KEY": dep.partner_key,
                "FILENAME": dep.filename,
                "PERIOD_LABEL": dep.period,
                "STATUS": dep.status,
                "LINE_COUNT": dep.line_count,
                "SUBMITTED_AT": dep.submitted_at,
            }
        )
    return rows[:limit]
