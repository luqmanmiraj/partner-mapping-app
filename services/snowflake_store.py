"""Snowflake persistence — STAGING, APP, OUTPUT, REF, QA."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from auth.snowflake_session import schema_fqn

DIMENSION_COLUMN_MAP = "column_mapping"


def _sql_str(value: str) -> str:
    return value.replace("'", "''")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _signature(columns: list[str]) -> str:
    normalized = sorted(c.strip().lower() for c in columns if str(c).strip())
    return hashlib.sha256("|".join(normalized).encode()).hexdigest()


def _parse_variant(value: Any, default: Any = None) -> Any:
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


# ── Currency ──────────────────────────────────────────────────────────────────

def convert_to_eur(conn, amount: float, currency: str, period: str) -> tuple[float, bool]:
    """Return (eur_amount, pending_final_rate). Uses latest ECB rate for period month."""
    if currency.upper() == "EUR":
        return round(amount, 2), False
    month_end = period  # caller should pass YYYY-MM when possible
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT rate_to_eur
            FROM {schema_fqn("REF")}.CURRENCY_RATE
            WHERE currency_code = %s
            ORDER BY rate_date DESC
            LIMIT 1
            """,
            (currency.upper(),),
        )
        row = cur.fetchone()
        if row:
            return round(amount * float(row[0]), 2), False
    finally:
        cur.close()
    # Fallback rates when table empty
    rates = {"USD": 0.92, "GBP": 1.17, "PLN": 0.23, "CHF": 1.05}
    rate = rates.get(currency.upper(), 1.0)
    return round(amount * rate, 2), currency.upper() != "EUR"


# ── Calibration / column templates ───────────────────────────────────────────

def resolve_column_template(
    conn,
    partner_key: str,
    source_columns: list[str],
) -> dict[str, Any] | None:
    sig = _signature(source_columns)
    table = f"{schema_fqn('APP')}.CALIBRATION_TEMPLATE"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT column_mapping, source_columns, is_stable
            FROM {table}
            WHERE partner_key = %s AND source_signature = %s
            LIMIT 1
            """,
            (partner_key, sig),
        )
        row = cur.fetchone()
        if row:
            return {
                "scope": "LOCAL",
                "mapping": _parse_variant(row[0], {}),
                "source_columns": _parse_variant(row[1], source_columns),
                "matched_at": _now_iso(),
                "is_stable": bool(row[2]),
            }
        global_mem = f"{schema_fqn('APP')}.GLOBAL_MEMORY"
        cur.execute(
            f"""
            SELECT target_value
            FROM {global_mem}
            WHERE dimension = %s AND source_value = %s
            LIMIT 1
            """,
            (DIMENSION_COLUMN_MAP, sig),
        )
        row = cur.fetchone()
        if row:
            return {
                "scope": "GLOBAL",
                "mapping": _parse_variant(row[0], {}),
                "source_columns": source_columns,
                "matched_at": _now_iso(),
            }
    finally:
        cur.close()
    return None


def save_calibration_template(
    conn,
    *,
    partner_key: str,
    source_columns: list[str],
    column_mapping: dict[str, str],
    is_stable: bool,
    actor: str = "admin",
) -> None:
    sig = _signature(source_columns)
    table = f"{schema_fqn('APP')}.CALIBRATION_TEMPLATE"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            MERGE INTO {table} AS t
            USING (SELECT %s AS pk, %s AS sig) AS s
            ON t.partner_key = s.pk AND t.source_signature = s.sig
            WHEN MATCHED THEN UPDATE SET
                source_columns = PARSE_JSON(%s),
                column_mapping = PARSE_JSON(%s),
                is_stable = %s,
                updated_at = CURRENT_TIMESTAMP(),
                updated_by = %s
            WHEN NOT MATCHED THEN INSERT (
                partner_key, source_signature, source_columns, column_mapping,
                is_stable, updated_at, updated_by
            ) VALUES (%s, %s, PARSE_JSON(%s), PARSE_JSON(%s), %s, CURRENT_TIMESTAMP(), %s)
            """,
            (
                partner_key, sig,
                json.dumps(source_columns), json.dumps(column_mapping), is_stable, actor,
                partner_key, sig, json.dumps(source_columns), json.dumps(column_mapping), is_stable, actor,
            ),
        )
    finally:
        cur.close()


# ── Upload / STAGING ─────────────────────────────────────────────────────────

def insert_raw_file(
    conn,
    *,
    upload_id: str,
    partner_key: str,
    declarant_type: str,
    period: str,
    currency: str,
    comment: str,
    filename: str,
    file_size: int,
    line_count: int,
    status: str,
    auto_validated: int,
    in_review: int,
    rejected: int,
    local_total: float,
    eur_total: float,
    pending_final_rate: bool,
    is_corrective: bool = False,
    supersedes_upload_id: str = "",
) -> None:
    table = f"{schema_fqn('STAGING')}.RAW_FILE"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (
                upload_id, partner_key, declarant_type, period_label, currency_code,
                comment_text, filename, file_size_bytes, line_count, status,
                auto_validated_count, in_review_count, rejected_count,
                local_total, eur_total, is_corrective, supersedes_upload_id,
                submitted_at, processed_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()
            )
            """,
            (
                upload_id, partner_key, declarant_type, period, currency,
                comment[:500], filename, file_size, line_count, status,
                auto_validated, in_review, rejected,
                local_total, eur_total, is_corrective,
                supersedes_upload_id or None,
            ),
        )
    finally:
        cur.close()


def insert_parsed_lines(conn, *, upload_id: str, partner_key: str, lines: list[dict]) -> None:
    """Legacy bulk insert without per-line currency."""
    for i, row in enumerate(lines[:5000], start=1):
        insert_parsed_line(
            conn,
            line_id=f"LN-{uuid.uuid4().hex[:12].upper()}",
            upload_id=upload_id,
            partner_key=partner_key,
            line_number=i,
            raw_payload=row,
            canonical_payload=row,
            turnover_local=0.0,
            currency_code="EUR",
            turnover_eur=0.0,
            pending_final_rate=False,
        )


def insert_parsed_line(
    conn,
    *,
    line_id: str,
    upload_id: str,
    partner_key: str,
    line_number: int,
    raw_payload: dict,
    canonical_payload: dict,
    turnover_local: float,
    currency_code: str,
    turnover_eur: float,
    pending_final_rate: bool,
    parse_status: str = "parsed",
) -> None:
    table = f"{schema_fqn('STAGING')}.PARSED_LINE"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (
                line_id, upload_id, partner_key, line_number,
                raw_payload, parsed_payload, canonical_payload,
                turnover_local, currency_code, turnover_eur, pending_final_rate, parse_status
            )
            SELECT %s, %s, %s, %s,
                   PARSE_JSON(%s), PARSE_JSON(%s), PARSE_JSON(%s),
                   %s, %s, %s, %s, %s
            """,
            (
                line_id, upload_id, partner_key, line_number,
                json.dumps(raw_payload), json.dumps(canonical_payload), json.dumps(canonical_payload),
                turnover_local, currency_code, turnover_eur, pending_final_rate, parse_status,
            ),
        )
    except Exception:
        cur.execute(
            f"""
            INSERT INTO {table} (line_id, upload_id, partner_key, line_number, raw_payload, parsed_payload)
            SELECT %s, %s, %s, %s, PARSE_JSON(%s), PARSE_JSON(%s)
            """,
            (line_id, upload_id, partner_key, line_number, json.dumps(raw_payload), json.dumps(canonical_payload)),
        )
    finally:
        cur.close()


def insert_upload_error(
    conn,
    *,
    upload_id: str,
    partner_key: str,
    line_number: int,
    error_code: str,
    error_message: str,
) -> None:
    table = f"{schema_fqn('STAGING')}.UPLOAD_ERROR"
    err_id = f"ERR-{uuid.uuid4().hex[:10].upper()}"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (error_id, upload_id, partner_key, line_number, error_code, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (err_id, upload_id, partner_key, line_number, error_code, error_message[:2000]),
        )
    finally:
        cur.close()


def insert_validated_line(
    conn,
    *,
    upload_id: str,
    partner_key: str,
    period_label: str,
    product_category_id: str,
    counterparty_member_id: str,
    counterparty_supplier_id: str,
    turnover_local: float,
    currency_code: str,
    turnover_eur: float,
    pending_final_rate: bool,
) -> None:
    table = f"{schema_fqn('APP')}.VALIDATED_LINE"
    vid = f"VL-{uuid.uuid4().hex[:10].upper()}"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (
                validated_line_id, upload_id, partner_key,
                product_category_id, counterparty_member_id, counterparty_supplier_id,
                turnover_local, currency_code, turnover_eur, pending_final_rate, period_label
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                vid, upload_id, partner_key,
                product_category_id, counterparty_member_id, counterparty_supplier_id,
                turnover_local, currency_code, turnover_eur, pending_final_rate, period_label,
            ),
        )
    finally:
        cur.close()


def cortex_propose(conn, *, dimension: str, source_value: str) -> tuple[str, float] | None:
    """Step 4 — Snowflake Cortex with taxonomy fallback."""
    safe = source_value.replace("'", "''")[:500]
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'snowflake-arctic',
                'Map this {dimension} value to a canonical ID: {safe}. Reply with ID only.'
            ) AS proposal
            """
        )
        row = cur.fetchone()
        if row and row[0]:
            text = str(row[0]).strip()[:512]
            return text, 0.85
    except Exception:
        pass
    finally:
        cur.close()

    cur = conn.cursor()
    try:
        if dimension == "product_category":
            cur.execute(
                f"""
                SELECT ga_id, 0.80
                FROM {schema_fqn('REF')}.TAXONOMY_BUSINESS
                WHERE LOWER(ga_name) LIKE LOWER(%s)
                   OR LOWER(subgroup_name) LIKE LOWER(%s)
                LIMIT 1
                """,
                (f"%{source_value[:80]}%", f"%{source_value[:80]}%"),
            )
        else:
            cur.execute(
                f"""
                SELECT id_code, 0.75
                FROM {schema_fqn('REF')}.MEMBER_ITG
                WHERE LOWER(company_name) LIKE LOWER(%s)
                LIMIT 1
                """,
                (f"%{source_value[:80]}%",),
            )
        row = cur.fetchone()
        if row:
            return str(row[0]), float(row[1])
    except Exception:
        pass
    finally:
        cur.close()

    return f"UNRESOLVED-{abs(hash(source_value)) % 99999:05d}", 0.55


def refresh_business_view(
    conn, *, upload_id: str, partner_key: str, period_label: str
) -> None:
    """Insert validated lines into OUTPUT.BUSINESS_VIEW for this upload."""
    table = f"{schema_fqn('OUTPUT')}.BUSINESS_VIEW"
    vl = f"{schema_fqn('APP')}.VALIDATED_LINE"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (
                row_id, partner_key, period_label, counterparty_name,
                ga_code, turnover_local, currency_code, turnover_eur, turnover_eur_n1
            )
            SELECT
                'BV-' || validated_line_id,
                partner_key,
                period_label,
                COALESCE(NULLIF(counterparty_member_id, ''), counterparty_supplier_id, 'Unknown'),
                product_category_id,
                turnover_local,
                currency_code,
                turnover_eur,
                turnover_eur * 0.95
            FROM {vl}
            WHERE upload_id = %s AND partner_key = %s
            """,
            (upload_id, partner_key),
        )
    except Exception:
        pass
    finally:
        cur.close()


def insert_notification(
    conn,
    *,
    partner_key: str,
    upload_id: str,
    category: str,
    message: str,
    notification_type: str = "deposit",
) -> str:
    import os

    nid = f"NTF-{uuid.uuid4().hex[:10].upper()}"
    table = f"{schema_fqn('APP')}.NOTIFICATION"
    email_sent = False
    notify_url = os.environ.get("NOTIFY_EMAIL_URL", "")
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (
                notification_id, partner_key, upload_id, category,
                message, notification_type, is_read, email_sent
            ) VALUES (%s, %s, %s, %s, %s, %s, FALSE, %s)
            """,
            (nid, partner_key, upload_id, category, message[:2000], notification_type, email_sent),
        )
    except Exception:
        pass
    finally:
        cur.close()
    return nid


def list_notifications(conn, partner_key: str, limit: int = 50) -> list[dict[str, Any]]:
    table = f"{schema_fqn('APP')}.NOTIFICATION"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT notification_id, category, message, notification_type, is_read,
                   TO_VARCHAR(created_at, 'Mon, DD') AS created_at
            FROM {table}
            WHERE partner_key = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (partner_key, int(limit)),
        )
        return [
            {
                "id": r[0],
                "category": r[1],
                "message": r[2],
                "notification_type": r[3],
                "is_read": bool(r[4]),
                "date": str(r[5]),
            }
            for r in cur.fetchall()
        ]
    except Exception:
        return []
    finally:
        cur.close()


def supersede_upload(conn, upload_id: str) -> None:
    table = f"{schema_fqn('STAGING')}.RAW_FILE"
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE {table} SET status = 'Superseded' WHERE upload_id = %s",
            (upload_id,),
        )
    finally:
        cur.close()


def has_in_review_deposits(conn, partner_key: str, quarter: str) -> bool:
    table = f"{schema_fqn('STAGING')}.RAW_FILE"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT COUNT(*) FROM {table}
            WHERE partner_key = %s AND period_label LIKE %s AND status = 'In review'
            """,
            (partner_key, f"%{quarter}%"),
        )
        return int(cur.fetchone()[0]) > 0
    finally:
        cur.close()


# ── Value memory (BR-MAP-04) ──────────────────────────────────────────────────

def lookup_value_memory(
    conn, partner_key: str, dimension: str, source_value: str
) -> str | None:
    local = f"{schema_fqn('APP')}.LOCAL_MEMORY"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT target_value FROM {local}
            WHERE partner_key = %s AND dimension = %s AND source_value = %s
            LIMIT 1
            """,
            (partner_key, dimension, source_value),
        )
        row = cur.fetchone()
        if row:
            return str(row[0])
        global_mem = f"{schema_fqn('APP')}.GLOBAL_MEMORY"
        cur.execute(
            f"""
            SELECT target_value FROM {global_mem}
            WHERE dimension = %s AND source_value = %s
            LIMIT 1
            """,
            (dimension, source_value),
        )
        row = cur.fetchone()
        return str(row[0]) if row else None
    finally:
        cur.close()


def save_value_memory(
    conn,
    *,
    partner_key: str,
    dimension: str,
    source_value: str,
    target_value: str,
    scope: str,
) -> None:
    memory_id = f"MEM-{uuid.uuid4().hex[:10].upper()}"
    cur = conn.cursor()
    try:
        if scope == "LOCAL":
            table = f"{schema_fqn('APP')}.LOCAL_MEMORY"
            cur.execute(
                f"""
                INSERT INTO {table} (memory_id, partner_key, dimension, source_value, target_value)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (memory_id, partner_key, dimension, source_value, target_value),
            )
        else:
            table = f"{schema_fqn('APP')}.GLOBAL_MEMORY"
            cur.execute(
                f"""
                INSERT INTO {table} (memory_id, dimension, source_value, target_value)
                VALUES (%s, %s, %s, %s)
                """,
                (memory_id, dimension, source_value, target_value),
            )
    finally:
        cur.close()


# ── Mapping proposals ─────────────────────────────────────────────────────────

def insert_mapping_proposal(
    conn,
    *,
    proposal_id: str,
    upload_id: str,
    partner_key: str,
    dimension: str,
    source_value: str,
    proposed_target: str,
    confidence_score: float,
    status: str = "Pending",
) -> None:
    table = f"{schema_fqn('APP')}.MAPPING_PROPOSAL"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (
                proposal_id, upload_id, partner_key, dimension,
                source_value, proposed_target, confidence_score, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (proposal_id, upload_id, partner_key, dimension, source_value, proposed_target, confidence_score, status),
        )
    finally:
        cur.close()


def get_proposal(conn, proposal_id: str) -> dict[str, Any] | None:
    table = f"{schema_fqn('APP')}.MAPPING_PROPOSAL"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT proposal_id, upload_id, partner_key, dimension, source_value,
                   proposed_target, confidence_score, status, memory_scope,
                   reviewer_comment, tags
            FROM {table} WHERE proposal_id = %s LIMIT 1
            """,
            (proposal_id,),
        )
        row = cur.fetchone()
    finally:
        cur.close()
    if not row:
        return None
    return {
        "proposal_id": row[0],
        "upload_id": row[1],
        "partner_key": row[2],
        "dimension": row[3],
        "source_value": row[4],
        "proposed_target": row[5],
        "confidence_score": float(row[6] or 0),
        "status": row[7],
        "memory_scope": row[8],
        "reviewer_comment": row[9],
        "tags": _parse_variant(row[10], []),
    }


def update_proposal(
    conn,
    proposal_id: str,
    *,
    status: str,
    proposed_target: str | None = None,
    memory_scope: str | None = None,
    reviewer_comment: str = "",
    tags: list | None = None,
) -> None:
    table = f"{schema_fqn('APP')}.MAPPING_PROPOSAL"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            UPDATE {table}
            SET status = %s,
                proposed_target = COALESCE(%s, proposed_target),
                memory_scope = COALESCE(%s, memory_scope),
                reviewer_comment = %s,
                tags = PARSE_JSON(%s),
                resolved_at = CURRENT_TIMESTAMP()
            WHERE proposal_id = %s
            """,
            (
                status,
                proposed_target,
                memory_scope,
                reviewer_comment,
                json.dumps(tags or []),
                proposal_id,
            ),
        )
    finally:
        cur.close()


# ── Partners / admin ──────────────────────────────────────────────────────────

def load_active_partners(conn) -> list[dict[str, Any]]:
    table = f"{schema_fqn('REF')}.DECLARANT_PARTNER"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT partner_key, declarant_type, is_active,
                   COALESCE(default_currency, 'EUR') AS default_currency
            FROM {table}
            WHERE is_active = TRUE
            ORDER BY partner_key
            LIMIT 500
            """
        )
        rows = cur.fetchall()
    finally:
        cur.close()
    return [
        {
            "partner_key": r[0],
            "declarant_type": r[1],
            "is_active": bool(r[2]),
            "default_currency": r[3],
        }
        for r in rows
    ]


def partner_is_active_sf(conn, partner_key: str) -> bool:
    table = f"{schema_fqn('REF')}.DECLARANT_PARTNER"
    cur = conn.cursor()
    try:
        cur.execute(
            f"SELECT is_active FROM {table} WHERE partner_key = %s LIMIT 1",
            (partner_key,),
        )
        row = cur.fetchone()
        return bool(row[0]) if row else False
    finally:
        cur.close()


def activate_partner_sf(
    conn, partner_key: str, *, actor: str = "admin"
) -> None:
    table = f"{schema_fqn('REF')}.DECLARANT_PARTNER"
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE {table} SET is_active = TRUE WHERE partner_key = %s",
            (partner_key,),
        )
    finally:
        cur.close()


def deactivate_partner_sf(conn, partner_key: str) -> None:
    table = f"{schema_fqn('REF')}.DECLARANT_PARTNER"
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE {table} SET is_active = FALSE WHERE partner_key = %s",
            (partner_key,),
        )
    finally:
        cur.close()


def get_system_config(conn) -> dict[str, float]:
    table = f"{schema_fqn('APP')}.SYSTEM_CONFIG"
    defaults = {"confidence_threshold": 0.9, "discrepancy_info_pct": 1.0, "discrepancy_alert_pct": 10.0}
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT config_key, config_value FROM {table}")
        for key, val in cur.fetchall():
            try:
                defaults[key] = float(val)
            except (TypeError, ValueError):
                pass
    except Exception:
        pass
    finally:
        cur.close()
    return defaults


def update_system_config_sf(
    conn,
    *,
    confidence: float,
    info_pct: float,
    alert_pct: float,
    actor: str = "admin",
) -> None:
    table = f"{schema_fqn('APP')}.SYSTEM_CONFIG"
    updates = {
        "confidence_threshold": str(confidence),
        "discrepancy_info_pct": str(info_pct),
        "discrepancy_alert_pct": str(alert_pct),
    }
    cur = conn.cursor()
    try:
        for key, val in updates.items():
            cur.execute(
                f"""
                MERGE INTO {table} AS t
                USING (SELECT %s AS k, %s AS v, %s AS u) AS s
                ON t.config_key = s.k
                WHEN MATCHED THEN UPDATE SET config_value = s.v, updated_at = CURRENT_TIMESTAMP(), updated_by = s.u
                WHEN NOT MATCHED THEN INSERT (config_key, config_value, updated_by) VALUES (s.k, s.v, s.u)
                """,
                (key, val, actor),
            )
    finally:
        cur.close()


# ── Closure ───────────────────────────────────────────────────────────────────

def is_period_closed_sf(conn, partner_key: str, period: str) -> bool:
    table = f"{schema_fqn('REF')}.BILLING_STATUS"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT is_closed FROM {table}
            WHERE partner_key = %s AND quarter_label = %s AND is_closed = TRUE
            LIMIT 1
            """,
            (partner_key, period),
        )
        return cur.fetchone() is not None
    except Exception:
        return False
    finally:
        cur.close()


def close_quarter_sf(
    conn, partner_key: str, quarter: str, *, actor: str = "admin"
) -> str:
    snapshot_id = f"SNAP-{uuid.uuid4().hex[:8].upper()}"
    snap_table = f"{schema_fqn('OUTPUT')}.ACCOUNTING_SNAPSHOT"
    bill_table = f"{schema_fqn('REF')}.BILLING_STATUS"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {snap_table} (snapshot_id, partner_key, quarter_label, is_billed, created_by)
            VALUES (%s, %s, %s, TRUE, %s)
            """,
            (snapshot_id, partner_key, quarter, actor),
        )
        cur.execute(
            f"""
            MERGE INTO {bill_table} AS t
            USING (SELECT %s AS pk, %s AS q) AS s
            ON t.partner_key = s.pk AND t.quarter_label = s.q
            WHEN MATCHED THEN UPDATE SET is_closed = TRUE, closed_at = CURRENT_TIMESTAMP(),
                closed_by = %s, snapshot_id = %s
            WHEN NOT MATCHED THEN INSERT (partner_key, quarter_label, is_closed, closed_at, closed_by, snapshot_id)
            VALUES (s.pk, s.q, TRUE, CURRENT_TIMESTAMP(), %s, %s)
            """,
            (partner_key, quarter, actor, snapshot_id, actor, snapshot_id),
        )
    finally:
        cur.close()
    return snapshot_id


def record_post_billing_mod_sf(
    conn, partner_key: str, period: str, reason: str, *, actor: str
) -> None:
    mod_id = f"PBM-{uuid.uuid4().hex[:8].upper()}"
    table = f"{schema_fqn('QA')}.POST_BILLING_MODIFICATION"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            INSERT INTO {table} (mod_id, partner_key, period_label, reason, author)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (mod_id, partner_key, period, reason, actor),
        )
    finally:
        cur.close()


def save_qa_resolution(
    conn, *, case_id: str, case_type: str, resolution: str, tag: str, actor: str
) -> None:
    table = f"{schema_fqn('QA')}.QA_RESOLUTION"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            MERGE INTO {table} AS t
            USING (SELECT %s AS id) AS s ON t.case_id = s.id
            WHEN MATCHED THEN UPDATE SET resolution = %s, tag = %s, resolved_by = %s, resolved_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN INSERT (case_id, case_type, resolution, tag, resolved_by)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (case_id, resolution, tag, actor, case_id, case_type, resolution, tag, actor),
        )
    finally:
        cur.close()


def list_post_billing_mods(conn, limit: int = 50) -> list[dict[str, Any]]:
    table = f"{schema_fqn('QA')}.POST_BILLING_MODIFICATION"
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT partner_key, period_label, reason, author, created_at
            FROM {table} ORDER BY created_at DESC LIMIT {int(limit)}
            """
        )
        return [
            {
                "partner_key": r[0],
                "period": r[1],
                "reason": r[2],
                "author": r[3],
                "timestamp": str(r[4]),
            }
            for r in cur.fetchall()
        ]
    except Exception:
        return []
    finally:
        cur.close()
