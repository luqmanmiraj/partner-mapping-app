"""Financial dashboard metrics from OUTPUT.BUSINESS_VIEW."""

from __future__ import annotations

import pandas as pd
import snowflake.connector

from auth.session import UserSession
from auth.snowflake_session import partner_key_filter, schema_fqn
from data import demo_fixtures
from snowflake_client import query_df


def load_financial_dashboard(
    session: UserSession,
    conn: snowflake.connector.SnowflakeConnection | None,
    *,
    granularity: str = "monthly",
) -> dict:
    if conn is None:
        data = demo_fixtures.financial_dashboard(session)
        data["source"] = "demo"
        return data

    pk_filter = partner_key_filter(session)
    try:
        monthly = query_df(
            conn,
            f"""
            SELECT
                period_label AS period,
                SUM(turnover_local) AS turnover_local,
                SUM(turnover_eur) AS turnover_eur,
                SUM(turnover_eur_n1) AS turnover_n1
            FROM {schema_fqn("OUTPUT")}.BUSINESS_VIEW
            WHERE {pk_filter}
            GROUP BY period_label
            ORDER BY period_label
            """,
        )
        cp_col = "counterparty_name"
        top = query_df(
            conn,
            f"""
            SELECT
                {cp_col} AS name,
                country_code AS country,
                SUM(turnover_eur) AS turnover_eur
            FROM {schema_fqn("OUTPUT")}.BUSINESS_VIEW
            WHERE {pk_filter}
            GROUP BY {cp_col}, country_code
            ORDER BY turnover_eur DESC
            LIMIT 10
            """,
        )
        totals = query_df(
            conn,
            f"""
            SELECT
                SUM(turnover_eur) AS total_eur,
                SUM(turnover_local) AS total_local,
                SUM(turnover_eur_n1) AS total_n1
            FROM {schema_fqn("OUTPUT")}.BUSINESS_VIEW
            WHERE {pk_filter}
            """,
        )
        total_eur = float(totals.iloc[0]["TOTAL_EUR"] if not totals.empty else 0)
        total_n1 = float(totals.iloc[0]["TOTAL_N1"] if not totals.empty else 0)
        delta_pct = ((total_eur - total_n1) / total_n1 * 100) if total_n1 else 0

        cp_label = session.counterparty_label.rstrip("s")
        top_display = pd.DataFrame()
        if not top.empty:
            top_display = top.rename(
                columns={"NAME": cp_label, "COUNTRY": "Country", "TURNOVER_EUR": "turnover_eur"}
            )
            top_display["Turnover (EUR)"] = top_display["turnover_eur"].apply(
                lambda v: f"€{v/1000:.0f}K" if v >= 1000 else f"€{v:.0f}"
            )
            total_top = top_display["turnover_eur"].sum() or 1
            top_display["Share"] = top_display["turnover_eur"].apply(
                lambda v: f"{v/total_top*100:.0f}%"
            )
            top_display = top_display[[cp_label, "Country", "Turnover (EUR)", "Share"]]

        return {
            "source": "snowflake",
            "overview_cards": [
                {
                    "label": "Cumulated Turnover (EUR)",
                    "value": f"€{total_eur/1_000_000:.2f}M" if total_eur >= 1_000_000 else f"€{total_eur:,.0f}",
                    "delta": f"{delta_pct:+.1f}% vs N-1",
                    "positive": delta_pct >= 0,
                },
                {
                    "label": f"Cumulated Turnover ({session.default_currency})",
                    "value": f"€{float(totals.iloc[0]['TOTAL_LOCAL'] if not totals.empty else 0):,.0f}",
                    "delta": "YTD",
                    "positive": True,
                },
                {
                    "label": "Validated Lines",
                    "value": "—",
                    "delta": "From OUTPUT",
                    "positive": True,
                },
                {
                    "label": f"Top {session.counterparty_label}",
                    "value": str(len(top_display)),
                    "delta": "Shown in EUR",
                    "positive": True,
                },
            ],
            "monthly": monthly,
            "top_counterparties": top_display if not top_display.empty else demo_fixtures.financial_dashboard(session)["top_counterparties"],
            "last_updated": "Live from Snowflake",
            "period_closed": False,
        }
    except Exception:
        data = demo_fixtures.financial_dashboard(session)
        data["source"] = "demo"
        return data
