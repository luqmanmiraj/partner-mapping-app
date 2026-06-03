"""Snowflake-backed memory + review workflow with session fallback."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

import streamlit as st

from auth.snowflake_session import schema_fqn

APP_SCHEMA = "APP"
_TABLES_READY_KEY = "snowflake_memory_tables_ready"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_columns(columns: list[str]) -> list[str]:
    clean = [str(c).strip() for c in columns if str(c).strip()]
    return list(dict.fromkeys(clean))


def _signature(columns: list[str]) -> str:
    normalized = sorted(c.lower() for c in _normalize_columns(columns))
    payload = "|".join(normalized).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sql_str(value: str) -> str:
    return value.replace("'", "''")


def _init_fallback_state() -> None:
    if "memory_review_entries" not in st.session_state:
        st.session_state.memory_review_entries = {}
    if "memory_global_templates" not in st.session_state:
        st.session_state.memory_global_templates = {}
    if "memory_local_templates" not in st.session_state:
        st.session_state.memory_local_templates = {}


def snowflake_enabled() -> bool:
    return bool(st.session_state.get("use_snowflake", False))


def _app_fqn(table: str) -> str:
    return f"{schema_fqn(APP_SCHEMA)}.{table}"


def ensure_memory_tables(conn) -> None:
    if st.session_state.get(_TABLES_READY_KEY):
        return

    review = _app_fqn("REVIEW_ENTRY")
    global_mem = _app_fqn("GLOBAL_MEMORY")
    local_mem = _app_fqn("LOCAL_MEMORY")

    statements = (
        f"""
        CREATE TABLE IF NOT EXISTS {review} (
            REVIEW_ID VARCHAR PRIMARY KEY,
            UPLOAD_ID VARCHAR NOT NULL,
            PARTNER_KEY VARCHAR NOT NULL,
            FILENAME VARCHAR,
            PERIOD VARCHAR,
            SOURCE_COLUMNS VARIANT,
            SOURCE_SIGNATURE VARCHAR NOT NULL,
            MAPPING VARIANT,
            STATUS VARCHAR NOT NULL,
            VALIDATION_SOURCE VARCHAR,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {global_mem} (
            SOURCE_SIGNATURE VARCHAR PRIMARY KEY,
            SOURCE_COLUMNS VARIANT,
            MAPPING VARIANT NOT NULL,
            CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_BY VARCHAR
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {local_mem} (
            PARTNER_KEY VARCHAR NOT NULL,
            SOURCE_SIGNATURE VARCHAR NOT NULL,
            SOURCE_COLUMNS VARIANT,
            MAPPING VARIANT NOT NULL,
            UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (PARTNER_KEY, SOURCE_SIGNATURE)
        )
        """,
    )

    cur = conn.cursor()
    try:
        for stmt in statements:
            cur.execute(stmt)
    finally:
        cur.close()
    st.session_state[_TABLES_READY_KEY] = True


def _parse_json_field(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
    return default


def resolve_template(
    partner_key: str,
    source_columns: list[str],
    conn=None,
) -> dict[str, Any] | None:
    sig = _signature(source_columns)
    normalized = _normalize_columns(source_columns)
    now = _now_iso()

    if conn is not None:
        ensure_memory_tables(conn)
        local = _app_fqn("LOCAL_MEMORY")
        global_mem = _app_fqn("GLOBAL_MEMORY")
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT MAPPING, SOURCE_COLUMNS
                FROM {local}
                WHERE PARTNER_KEY = %s AND SOURCE_SIGNATURE = %s
                LIMIT 1
                """,
                (partner_key, sig),
            )
            row = cur.fetchone()
            if row:
                return {
                    "scope": "LOCAL",
                    "mapping": _parse_json_field(row[0], {}),
                    "source_columns": _parse_json_field(row[1], normalized),
                    "matched_at": now,
                }

            cur.execute(
                f"""
                SELECT MAPPING, SOURCE_COLUMNS
                FROM {global_mem}
                WHERE SOURCE_SIGNATURE = %s
                LIMIT 1
                """,
                (sig,),
            )
            row = cur.fetchone()
            if row:
                return {
                    "scope": "GLOBAL",
                    "mapping": _parse_json_field(row[0], {}),
                    "source_columns": _parse_json_field(row[1], normalized),
                    "matched_at": now,
                }
        finally:
            cur.close()
        return None

    _init_fallback_state()
    local_key = f"{partner_key}:{sig}"
    local = st.session_state.memory_local_templates.get(local_key)
    if local:
        return {
            "scope": "LOCAL",
            "mapping": local.get("mapping", {}),
            "source_columns": local.get("source_columns", normalized),
            "matched_at": now,
        }
    global_template = st.session_state.memory_global_templates.get(sig)
    if global_template:
        return {
            "scope": "GLOBAL",
            "mapping": global_template.get("mapping", {}),
            "source_columns": global_template.get("source_columns", normalized),
            "matched_at": now,
        }
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
    normalized = _normalize_columns(source_columns)
    sig = _signature(normalized)
    review_id = f"REV-{uuid.uuid4().hex[:12].upper()}"
    mapping_payload = mapping or {}
    now = _now_iso()

    if conn is not None:
        ensure_memory_tables(conn)
        table = _app_fqn("REVIEW_ENTRY")
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                INSERT INTO {table} (
                    REVIEW_ID, UPLOAD_ID, PARTNER_KEY, FILENAME, PERIOD,
                    SOURCE_COLUMNS, SOURCE_SIGNATURE, MAPPING, STATUS,
                    VALIDATION_SOURCE, CREATED_AT, UPDATED_AT
                )
                SELECT
                    %s, %s, %s, %s, %s,
                    PARSE_JSON(%s), %s, PARSE_JSON(%s), %s,
                    %s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
                """,
                (
                    review_id,
                    upload_id,
                    partner_key,
                    filename,
                    period,
                    json.dumps(normalized),
                    sig,
                    json.dumps(mapping_payload),
                    status,
                    validation_source,
                ),
            )
        finally:
            cur.close()
        return review_id

    _init_fallback_state()
    doc = {
        "_id": review_id,
        "upload_id": upload_id,
        "partner_key": partner_key,
        "filename": filename,
        "period": period,
        "source_columns": normalized,
        "source_signature": sig,
        "mapping": mapping_payload,
        "status": status,
        "validation_source": validation_source,
        "created_at": now,
        "updated_at": now,
    }
    st.session_state.memory_review_entries[review_id] = doc
    return review_id


def list_review_entries(
    *,
    conn=None,
    status_filter: str = "All",
    partner_filter: str = "All",
) -> list[dict[str, Any]]:
    if conn is not None:
        ensure_memory_tables(conn)
        table = _app_fqn("REVIEW_ENTRY")
        clauses: list[str] = []
        if status_filter != "All":
            clauses.append(f"STATUS = '{_sql_str(status_filter)}'")
        if partner_filter != "All":
            clauses.append(f"PARTNER_KEY = '{_sql_str(partner_filter)}'")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT REVIEW_ID, UPLOAD_ID, PARTNER_KEY, FILENAME, PERIOD,
                       SOURCE_COLUMNS, MAPPING, STATUS, VALIDATION_SOURCE,
                       CREATED_AT, UPDATED_AT
                FROM {table}
                {where}
                ORDER BY CREATED_AT DESC
                LIMIT 200
                """
            )
            rows = cur.fetchall()
        finally:
            cur.close()

        items: list[dict[str, Any]] = []
        for row in rows:
            items.append(
                {
                    "_id": row[0],
                    "upload_id": row[1],
                    "partner_key": row[2],
                    "filename": row[3],
                    "period": row[4],
                    "source_columns": _parse_json_field(row[5], []),
                    "mapping": _parse_json_field(row[6], {}),
                    "status": row[7],
                    "validation_source": row[8],
                    "created_at": str(row[9] or ""),
                    "updated_at": str(row[10] or ""),
                }
            )
        return items

    _init_fallback_state()
    items = list(st.session_state.memory_review_entries.values())
    if status_filter != "All":
        items = [i for i in items if i.get("status") == status_filter]
    if partner_filter != "All":
        items = [i for i in items if i.get("partner_key") == partner_filter]
    return sorted(items, key=lambda i: i.get("created_at", ""), reverse=True)


def get_review_entry(review_id: str, conn=None) -> dict[str, Any] | None:
    if conn is not None:
        ensure_memory_tables(conn)
        table = _app_fqn("REVIEW_ENTRY")
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT REVIEW_ID, UPLOAD_ID, PARTNER_KEY, FILENAME, PERIOD,
                       SOURCE_COLUMNS, MAPPING, STATUS, VALIDATION_SOURCE,
                       CREATED_AT, UPDATED_AT
                FROM {table}
                WHERE REVIEW_ID = %s
                LIMIT 1
                """,
                (review_id,),
            )
            row = cur.fetchone()
        finally:
            cur.close()
        if not row:
            return None
        return {
            "_id": row[0],
            "upload_id": row[1],
            "partner_key": row[2],
            "filename": row[3],
            "period": row[4],
            "source_columns": _parse_json_field(row[5], []),
            "mapping": _parse_json_field(row[6], {}),
            "status": row[7],
            "validation_source": row[8],
            "created_at": str(row[9] or ""),
            "updated_at": str(row[10] or ""),
        }

    _init_fallback_state()
    return st.session_state.memory_review_entries.get(review_id)


def save_global_template(
    *,
    review_id: str,
    mapping: dict[str, str],
    reviewer: str = "reviewer",
    conn=None,
) -> None:
    review = get_review_entry(review_id, conn=conn)
    if not review:
        return

    source_columns = review.get("source_columns", [])
    sig = _signature(source_columns)
    normalized = _normalize_columns(source_columns)
    now = _now_iso()

    if conn is not None:
        ensure_memory_tables(conn)
        global_mem = _app_fqn("GLOBAL_MEMORY")
        review_table = _app_fqn("REVIEW_ENTRY")
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                MERGE INTO {global_mem} AS target
                USING (
                    SELECT
                        %s AS SOURCE_SIGNATURE,
                        PARSE_JSON(%s) AS SOURCE_COLUMNS,
                        PARSE_JSON(%s) AS MAPPING,
                        %s AS UPDATED_BY
                ) AS source
                ON target.SOURCE_SIGNATURE = source.SOURCE_SIGNATURE
                WHEN MATCHED THEN UPDATE SET
                    SOURCE_COLUMNS = source.SOURCE_COLUMNS,
                    MAPPING = source.MAPPING,
                    UPDATED_AT = CURRENT_TIMESTAMP(),
                    UPDATED_BY = source.UPDATED_BY
                WHEN NOT MATCHED THEN INSERT (
                    SOURCE_SIGNATURE, SOURCE_COLUMNS, MAPPING,
                    CREATED_AT, UPDATED_AT, UPDATED_BY
                ) VALUES (
                    source.SOURCE_SIGNATURE, source.SOURCE_COLUMNS, source.MAPPING,
                    CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP(), source.UPDATED_BY
                )
                """,
                (
                    sig,
                    json.dumps(normalized),
                    json.dumps(mapping),
                    reviewer,
                ),
            )
            cur.execute(
                f"""
                UPDATE {review_table}
                SET MAPPING = PARSE_JSON(%s),
                    STATUS = 'Validated',
                    VALIDATION_SOURCE = 'GLOBAL_MEMORY',
                    UPDATED_AT = CURRENT_TIMESTAMP()
                WHERE REVIEW_ID = %s
                """,
                (json.dumps(mapping), review_id),
            )
        finally:
            cur.close()
        return

    _init_fallback_state()
    st.session_state.memory_global_templates[sig] = {
        "source_columns": normalized,
        "mapping": mapping,
        "updated_at": now,
    }
    if review_id in st.session_state.memory_review_entries:
        entry = st.session_state.memory_review_entries[review_id]
        entry["mapping"] = mapping
        entry["status"] = "Validated"
        entry["validation_source"] = "GLOBAL_MEMORY"
        entry["updated_at"] = now
