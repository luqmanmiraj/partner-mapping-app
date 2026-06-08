"""Snowflake memory + calibration — delegates to snowflake_store (migration 001 schema)."""

from __future__ import annotations

import uuid
from typing import Any

import streamlit as st

from services import snowflake_store


def snowflake_enabled() -> bool:
    return bool(st.session_state.get("use_snowflake", False))


def resolve_template(
    partner_key: str,
    source_columns: list[str],
    conn=None,
) -> dict[str, Any] | None:
    if conn is not None:
        return snowflake_store.resolve_column_template(conn, partner_key, source_columns)
    return None


def create_review_entry(
    *,
    upload_id: str,
    partner_key: str,
    filename: str,
    period: str,
    source_columns: list[str],
    status: str,
    validation_source: str,
    mapping: dict[str, str] | None = None,
    conn=None,
) -> str:
    """Persist review queue metadata in session; optional Snowflake calibration write."""
    from datetime import datetime, timezone

    from services.brd_state import init_brd_state

    if conn is not None and mapping:
        snowflake_store.save_calibration_template(
            conn,
            partner_key=partner_key,
            source_columns=source_columns,
            column_mapping=mapping,
            is_stable=status == "Validated",
            actor=partner_key,
        )

    review_id = f"REV-{upload_id}"
    init_brd_state()
    st.session_state.review_entries[review_id] = {
        "_id": review_id,
        "upload_id": upload_id,
        "partner_key": partner_key,
        "filename": filename,
        "period": period,
        "source_columns": list(source_columns),
        "mapping": dict(mapping or {}),
        "status": status,
        "validation_source": validation_source,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "pending_proposals": 0,
    }
    return review_id


def _session_review_entries(
    *,
    status_filter: str = "All",
    partner_filter: str = "All",
) -> list[dict[str, Any]]:
    from services.brd_state import get_deposit, init_brd_state, list_proposals

    init_brd_state()
    entries: dict[str, dict[str, Any]] = {}

    for entry in st.session_state.review_entries.values():
        entries[entry["upload_id"]] = dict(entry)

    for dep in st.session_state.deposits.values():
        if dep.in_review > 0 or dep.status == "In review":
            rid = f"REV-{dep.upload_id}"
            entries.setdefault(
                dep.upload_id,
                {
                    "_id": rid,
                    "upload_id": dep.upload_id,
                    "partner_key": dep.partner_key,
                    "filename": dep.filename,
                    "period": dep.period,
                    "source_columns": [],
                    "mapping": {},
                    "status": dep.status,
                    "validation_source": "UPLOAD",
                    "created_at": dep.submitted_at,
                    "pending_proposals": dep.in_review,
                },
            )

    pending = [p for p in list_proposals() if p.status == "Pending"]
    for prop in pending:
        base = entries.get(prop.upload_id)
        if base:
            base["pending_proposals"] = int(base.get("pending_proposals", 0)) + 1
            if base["status"] not in ("Validated", "Rejected"):
                base["status"] = "In review"
        else:
            entries[prop.upload_id] = {
                "_id": f"REV-{prop.upload_id}",
                "upload_id": prop.upload_id,
                "partner_key": prop.partner_key,
                "filename": "",
                "period": "",
                "source_columns": [],
                "mapping": {},
                "status": "In review",
                "validation_source": "MAPPING_PROPOSAL",
                "created_at": "",
                "pending_proposals": 1,
            }

    items = list(entries.values())
    if partner_filter != "All":
        items = [e for e in items if e.get("partner_key") == partner_filter]
    if status_filter != "All":
        items = [e for e in items if e.get("status") == status_filter]
    elif status_filter == "All":
        items = [
            e
            for e in items
            if e.get("status") in ("In review", "Pending processing")
            or int(e.get("pending_proposals", 0)) > 0
        ]
    return sorted(items, key=lambda e: e.get("created_at", ""), reverse=True)


def list_review_entries(
    *,
    conn=None,
    status_filter: str = "All",
    partner_filter: str = "All",
) -> list[dict[str, Any]]:
    """Uploaded files waiting for review — Snowflake RAW_FILE + session fallback."""
    session_items = _session_review_entries(
        status_filter=status_filter, partner_filter=partner_filter
    )
    if conn is None:
        return session_items

    from auth.snowflake_session import schema_fqn
    from snowflake_client import query_df

    clauses = ["(in_review_count > 0 OR status = 'In review')"]
    if partner_filter != "All":
        safe = partner_filter.replace("'", "''")
        clauses.append(f"partner_key = '{safe}'")
    if status_filter != "All":
        clauses.append(f"status = '{status_filter.replace(chr(39), chr(39)*2)}'")
    where = " AND ".join(clauses)
    try:
        df = query_df(
            conn,
            f"""
            SELECT upload_id, partner_key, filename, period_label, status,
                   TO_VARCHAR(submitted_at, 'YYYY-MM-DD HH24:MI UTC') AS submitted_at,
                   in_review_count
            FROM {schema_fqn('STAGING')}.RAW_FILE
            WHERE {where}
            ORDER BY submitted_at DESC
            LIMIT 100
            """,
        )
    except Exception:
        return session_items

    by_upload = {e["upload_id"]: e for e in session_items}
    for _, row in df.iterrows():
        upload_id = str(row.get("UPLOAD_ID", row.get("upload_id", "")))
        review_id = f"REV-{upload_id}"
        existing = by_upload.get(upload_id, {})
        by_upload[upload_id] = {
            "_id": review_id,
            "upload_id": upload_id,
            "partner_key": str(row.get("PARTNER_KEY", row.get("partner_key", ""))),
            "filename": str(row.get("FILENAME", row.get("filename", "")) or existing.get("filename", "")),
            "period": str(row.get("PERIOD_LABEL", row.get("period_label", "")) or existing.get("period", "")),
            "source_columns": existing.get("source_columns", []),
            "mapping": existing.get("mapping", {}),
            "status": str(row.get("STATUS", row.get("status", "In review"))),
            "validation_source": existing.get("validation_source", "SNOWFLAKE"),
            "created_at": str(row.get("SUBMITTED_AT", row.get("submitted_at", ""))),
            "pending_proposals": int(row.get("IN_REVIEW_COUNT", row.get("in_review_count", 0)) or 0),
        }

    items = list(by_upload.values())
    if status_filter == "All":
        items = [
            e
            for e in items
            if e.get("status") in ("In review", "Pending processing")
            or int(e.get("pending_proposals", 0)) > 0
        ]
    return sorted(items, key=lambda e: e.get("created_at", ""), reverse=True)


def get_review_entry(review_id: str, conn=None) -> dict[str, Any] | None:
    from services.brd_state import get_proposal, init_brd_state

    init_brd_state()
    if review_id in st.session_state.review_entries:
        return dict(st.session_state.review_entries[review_id])

    upload_id = review_id.removeprefix("REV-")
    session_key = f"REV-{upload_id}"
    if session_key in st.session_state.review_entries:
        return dict(st.session_state.review_entries[session_key])

    p = get_proposal(review_id)
    if p:
        base = st.session_state.review_entries.get(f"REV-{p.upload_id}", {})
        return {
            "_id": review_id,
            "upload_id": p.upload_id,
            "partner_key": p.partner_key,
            "filename": base.get("filename", ""),
            "period": base.get("period", ""),
            "source_columns": base.get("source_columns", []),
            "status": p.status,
            "validation_source": "MAPPING_PROPOSAL",
            "mapping": {p.dimension: p.proposed_target, **base.get("mapping", {})},
        }

    if conn is not None:
        row = snowflake_store.get_proposal(conn, review_id)
        if row:
            base = st.session_state.review_entries.get(f"REV-{row['upload_id']}", {})
            return {
                "_id": review_id,
                "upload_id": row["upload_id"],
                "partner_key": row["partner_key"],
                "filename": base.get("filename", ""),
                "period": base.get("period", ""),
                "source_columns": base.get("source_columns", []),
                "status": row["status"],
                "validation_source": "MAPPING_PROPOSAL",
                "mapping": {row["dimension"]: row["proposed_target"], **base.get("mapping", {})},
            }
        from auth.snowflake_session import schema_fqn
        from snowflake_client import query_df

        try:
            safe_id = upload_id.replace("'", "''")
            df = query_df(
                conn,
                f"""
                SELECT upload_id, partner_key, filename, period_label, status
                FROM {schema_fqn('STAGING')}.RAW_FILE
                WHERE upload_id = '{safe_id}'
                LIMIT 1
                """,
            )
            if not df.empty:
                row = df.iloc[0]
                base = st.session_state.review_entries.get(session_key, {})
                cols = base.get("source_columns", [])
                if not cols:
                    tmpl = snowflake_store.resolve_column_template(conn, str(row.get("PARTNER_KEY", row.get("partner_key", ""))), [])
                    if tmpl and tmpl.get("mapping"):
                        cols = list(tmpl["mapping"].keys())
                return {
                    "_id": session_key,
                    "upload_id": upload_id,
                    "partner_key": str(row.get("PARTNER_KEY", row.get("partner_key", ""))),
                    "filename": str(row.get("FILENAME", row.get("filename", ""))),
                    "period": str(row.get("PERIOD_LABEL", row.get("period_label", ""))),
                    "source_columns": cols,
                    "mapping": base.get("mapping", {}),
                    "status": str(row.get("STATUS", row.get("status", "In review"))),
                    "validation_source": base.get("validation_source", "SNOWFLAKE"),
                }
        except Exception:
            pass

    return None


def save_global_template(
    *,
    review_id: str,
    mapping: dict[str, str],
    reviewer: str = "reviewer",
    conn=None,
) -> None:
    if conn is None:
        return
    p = snowflake_store.get_proposal(conn, review_id)
    if not p:
        return
    for dim, target in mapping.items():
        snowflake_store.save_value_memory(
            conn,
            partner_key=p["partner_key"],
            dimension=dim,
            source_value=p["source_value"],
            target_value=target,
            scope="GLOBAL",
        )
    snowflake_store.update_proposal(
        conn, review_id, status="Validated", memory_scope="GLOBAL", reviewer_comment="Global template saved"
    )
