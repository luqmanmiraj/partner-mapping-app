"""Declaration history and detail — BRD store + optional Snowflake."""

from __future__ import annotations

import pandas as pd

from auth.session import UserSession
from services.brd_state import get_deposit, is_period_closed, list_deposits, init_brd_state


def load_deposit_history(session: UserSession, conn=None) -> pd.DataFrame:
    init_brd_state()
    if conn is not None:
        from auth.snowflake_session import partner_key_filter, schema_fqn
        from snowflake_client import query_df

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
        except Exception:
            pass

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
    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["Deposit ID", "Period", "Submitted", "Currency", "Lines", "Status"]
    )


def load_deposit_detail(deposit_id: str, session: UserSession, conn=None) -> dict:
    init_brd_state()
    d = get_deposit(deposit_id)
    if not d:
        from data import demo_fixtures

        return demo_fixtures.deposit_detail(deposit_id, session)
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


def check_period_closed(partner_key: str, period: str) -> bool:
    return is_period_closed(partner_key, period)
