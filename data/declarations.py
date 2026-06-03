"""Declaration history and detail queries."""

from __future__ import annotations

import pandas as pd
import snowflake.connector

from auth.session import UserSession
from auth.snowflake_session import partner_key_filter, schema_fqn
from data import demo_fixtures
from snowflake_client import query_df


def load_deposit_history(
    session: UserSession,
    conn: snowflake.connector.SnowflakeConnection | None,
) -> pd.DataFrame:
    if conn is None:
        return demo_fixtures.deposit_history(session)

    pk_filter = partner_key_filter(session)
    sql = f"""
        SELECT
            upload_id AS "Deposit ID",
            period_label AS "Period",
            TO_VARCHAR(submitted_at, 'YYYY-MM-DD HH24:MI') AS "Submitted",
            currency_code AS "Currency",
            line_count AS "Lines",
            status AS "Status"
        FROM {schema_fqn("STAGING")}.RAW_FILE
        WHERE {pk_filter}
        ORDER BY submitted_at DESC
        LIMIT 50
    """
    try:
        return query_df(conn, sql)
    except Exception:
        return demo_fixtures.deposit_history(session)


def load_deposit_detail(
    deposit_id: str,
    session: UserSession,
    conn: snowflake.connector.SnowflakeConnection | None,
) -> dict:
    if conn is None:
        return demo_fixtures.deposit_detail(deposit_id, session)

    pk_filter = partner_key_filter(session)
    sql = f"""
        SELECT
            upload_id,
            period_label,
            status,
            submitted_at,
            currency_code,
            auto_validated_count,
            in_review_count,
            rejected_count,
            local_total,
            eur_total
        FROM {schema_fqn("STAGING")}.RAW_FILE
        WHERE upload_id = '{deposit_id.replace("'", "''")}'
          AND {pk_filter}
        LIMIT 1
    """
    try:
        df = query_df(conn, sql)
        if df.empty:
            return demo_fixtures.deposit_detail(deposit_id, session)
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
        }
    except Exception:
        return demo_fixtures.deposit_detail(deposit_id, session)


def is_period_closed(period: str) -> bool:
    return period in demo_fixtures.CLOSED_PERIODS
