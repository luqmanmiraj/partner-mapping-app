"""Declaration history and detail — Snowflake STAGING with demo fallback."""

from __future__ import annotations

import streamlit as st

import pandas as pd

from auth.session import UserSession
from auth.snowflake_session import partner_key_filter, schema_fqn
from snowflake_client import query_df


def _snowflake_error() -> str:
    return st.session_state.get("snowflake_error", "")


def load_deposit_history(session: UserSession, conn=None) -> pd.DataFrame:
    if conn is not None:
        pk_filter = partner_key_filter(session)
        sql = f"""
            SELECT upload_id AS "Deposit ID", period_label AS "Period",
                   TO_VARCHAR(submitted_at, 'YYYY-MM-DD HH24:MI') AS "Submitted",
                   currency_code AS "Currency", line_count AS "Lines", status AS "Status"
            FROM {schema_fqn("STAGING")}.RAW_FILE
            WHERE {pk_filter}
            ORDER BY submitted_at DESC LIMIT 50
        """
        try:
            return query_df(conn, sql)
        except Exception as exc:
            st.session_state.snowflake_error = f"Deposit history query failed: {exc}"

    from services.brd_state import init_brd_state, list_deposits

    init_brd_state()
    rows = []
    for d in list_deposits(session.partner_key):
        rows.append(
            {
                "Deposit ID": d.upload_id,
                "Period": d.period,
                "Submitted": d.submitted_at,
                "Currency": d.currency,
                "Lines": d.line_count,
                "Status": d.status,
            }
        )
    if rows:
        return pd.DataFrame(rows)
    if _snowflake_error():
        return pd.DataFrame(columns=["Deposit ID", "Period", "Submitted", "Currency", "Lines", "Status"])
    from data import demo_fixtures

    return demo_fixtures.deposit_history(session)


def load_deposit_detail(deposit_id: str, session: UserSession, conn=None) -> dict:
    if conn is not None:
        pk_filter = partner_key_filter(session)
        safe_id = deposit_id.replace("'", "''")
        sql = f"""
            SELECT upload_id, period_label, status,
                   TO_VARCHAR(submitted_at, 'YYYY-MM-DD HH24:MI') AS submitted_at,
                   currency_code, auto_validated_count, in_review_count, rejected_count,
                   local_total, eur_total, comment_text
            FROM {schema_fqn("STAGING")}.RAW_FILE
            WHERE upload_id = '{safe_id}' AND {pk_filter}
            LIMIT 1
        """
        try:
            df = query_df(conn, sql)
            if not df.empty:
                row = df.iloc[0]
                return {
                    "deposit_id": str(row.get("UPLOAD_ID", row.get("upload_id", deposit_id))),
                    "period": str(row.get("PERIOD_LABEL", row.get("period_label", ""))),
                    "status": str(row.get("STATUS", row.get("status", ""))),
                    "submitted_at": str(row.get("SUBMITTED_AT", row.get("submitted_at", ""))),
                    "currency": str(row.get("CURRENCY_CODE", row.get("currency_code", "EUR"))),
                    "auto_validated": int(row.get("AUTO_VALIDATED_COUNT", row.get("auto_validated_count", 0))),
                    "in_review": int(row.get("IN_REVIEW_COUNT", row.get("in_review_count", 0))),
                    "rejected": int(row.get("REJECTED_COUNT", row.get("rejected_count", 0))),
                    "rejection_reasons": [],
                    "local_total": float(row.get("LOCAL_TOTAL", row.get("local_total", 0))),
                    "eur_total": float(row.get("EUR_TOTAL", row.get("eur_total", 0))),
                    "reconciled_csv": "",
                    "pending_final_rate": False,
                }
        except Exception as exc:
            st.session_state.snowflake_error = f"Deposit detail query failed: {exc}"

    from services.brd_state import get_deposit, init_brd_state

    init_brd_state()
    d = get_deposit(deposit_id)
    if d:
        return {
            "deposit_id": d.upload_id,
            "period": d.period,
            "status": d.status,
            "submitted_at": d.submitted_at,
            "currency": d.currency,
            "auto_validated": d.auto_validated,
            "in_review": d.in_review,
            "rejected": d.rejected,
            "rejection_reasons": d.rejection_reasons,
            "local_total": d.local_total,
            "eur_total": d.eur_total,
            "reconciled_csv": d.reconciled_csv,
            "pending_final_rate": d.pending_final_rate,
        }
    from data import demo_fixtures

    return demo_fixtures.deposit_detail(deposit_id, session)


def check_period_closed(partner_key: str, period: str, conn=None) -> bool:
    if conn is not None:
        from services.snowflake_store import is_period_closed_sf

        return is_period_closed_sf(conn, partner_key, period)
    from services.brd_state import is_period_closed

    return is_period_closed(partner_key, period)
