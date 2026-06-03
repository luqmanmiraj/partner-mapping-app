"""Load dashboard metrics from PM_PROD.REF on the destination Snowflake account."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import pandas as pd
import snowflake.connector

from snowflake_client import DATABASE, SCHEMA, pick_column, query_df, table_columns

FQN = f"{DATABASE}.{SCHEMA}"


@dataclass
class DashboardData:
    source: str = "demo"
    last_updated: str = ""
    overview_cards: list[dict] = field(default_factory=list)
    region_chart: pd.DataFrame = field(default_factory=pd.DataFrame)
    country_chart: pd.DataFrame = field(default_factory=pd.DataFrame)
    partners: pd.DataFrame = field(default_factory=pd.DataFrame)
    error: str | None = None


def _format_count(value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M".replace(".0M", "M")
    if value >= 1_000:
        return f"{value / 1_000:.1f}K".replace(".0K", "K")
    return str(value)


def _pct(part: int, whole: int) -> str:
    if whole <= 0:
        return "—"
    return f"{round(part / whole * 100)}%"


def _active_filter(columns: dict[str, str]) -> str:
    if "leave_date" in columns:
        return f"{columns['leave_date']} IS NULL"
    return "1=1"


def load_from_snowflake(conn: snowflake.connector.SnowflakeConnection) -> DashboardData:
    ts = query_df(conn, "SELECT TO_VARCHAR(CURRENT_TIMESTAMP(), 'YYYY-MM-DD HH24:MI TZHTZM') AS ts")
    last_updated = str(ts.iloc[0, 0]) if not ts.empty else "Unknown"

    members = int(query_df(conn, f"SELECT COUNT(*) AS c FROM {FQN}.MEMBER_ITG").iloc[0, 0])
    suppliers = int(query_df(conn, f"SELECT COUNT(*) AS c FROM {FQN}.SUPPLIER").iloc[0, 0])
    member_hubspot = int(query_df(conn, f"SELECT COUNT(*) AS c FROM {FQN}.MEMBER_HUBSPOT").iloc[0, 0])
    supplier_hubspot = int(query_df(conn, f"SELECT COUNT(*) AS c FROM {FQN}.SUPPLIER_HUBSPOT").iloc[0, 0])
    declarants = int(query_df(conn, f"SELECT COUNT(*) AS c FROM {FQN}.DECLARANT_PARTNER").iloc[0, 0])

    decl_cols = table_columns(conn, "DECLARANT_PARTNER")
    active_col = pick_column(decl_cols, "is_active", "IS_ACTIVE")
    if active_col:
        active_declarants = int(
            query_df(
                conn,
                f"SELECT COUNT(*) AS c FROM {FQN}.DECLARANT_PARTNER WHERE {active_col} = TRUE",
            ).iloc[0, 0]
        )
    else:
        active_declarants = 0

    member_cols = table_columns(conn, "MEMBER_ITG")
    geo_cols = table_columns(conn, "GEOGRAPHY")
    active_members = int(
        query_df(
            conn,
            f"SELECT COUNT(*) AS c FROM {FQN}.MEMBER_ITG WHERE {_active_filter(member_cols)}",
        ).iloc[0, 0]
    )

    hubspot_total = member_hubspot + supplier_hubspot
    overview_cards = [
        {
            "label": "Active Members",
            "value": _format_count(active_members),
            "delta": _pct(active_members, members),
            "positive": active_members >= members * 0.9,
        },
        {
            "label": "Suppliers",
            "value": _format_count(suppliers),
            "delta": f"{supplier_hubspot} mapped",
            "positive": supplier_hubspot > 0,
        },
        {
            "label": "HubSpot Links",
            "value": _format_count(hubspot_total),
            "delta": _pct(member_hubspot, members),
            "positive": member_hubspot >= members * 0.8,
        },
        {
            "label": "Active Partners",
            "value": _format_count(active_declarants),
            "delta": _pct(active_declarants, declarants) if declarants else "—",
            "positive": active_declarants > 0,
        },
    ]

    name_col = pick_column(member_cols, "company_name", "member_name", "company_path", "name")
    country_col = pick_column(
        member_cols,
        "country_code",
        "iso_country_code",
        "country_iso_code",
        "iso_code",
        "country",
    )
    geo_country_col = pick_column(geo_cols, "country_code", "iso_code", "iso_country_code")
    geo_name_col = pick_column(geo_cols, "country_name", "name")
    geo_region_col = pick_column(geo_cols, "region", "grouping_region", "region_name")

    region_chart = pd.DataFrame(columns=["region", "member_count"])
    country_chart = pd.DataFrame(columns=["country", "member_count"])
    partners = pd.DataFrame(columns=["Member", "Country", "Volume", "Growth", "positive"])

    if country_col and geo_country_col and geo_name_col and geo_region_col:
        region_chart = query_df(
            conn,
            f"""
            SELECT g.{geo_region_col} AS region, COUNT(*) AS member_count
              FROM {FQN}.MEMBER_ITG m
              JOIN {FQN}.GEOGRAPHY g ON m.{country_col} = g.{geo_country_col}
             WHERE {_active_filter(member_cols)}
             GROUP BY g.{geo_region_col}
             ORDER BY member_count DESC
            """,
        )
        country_chart = query_df(
            conn,
            f"""
            SELECT g.{geo_name_col} AS country, COUNT(*) AS member_count
              FROM {FQN}.MEMBER_ITG m
              JOIN {FQN}.GEOGRAPHY g ON m.{country_col} = g.{geo_country_col}
             WHERE {_active_filter(member_cols)}
             GROUP BY g.{geo_name_col}
             ORDER BY member_count DESC
             LIMIT 8
            """,
        )

    if name_col and country_col and geo_country_col and geo_name_col:
        name_expr = f"m.{name_col}"
        partners = query_df(
            conn,
            f"""
            SELECT
                {name_expr} AS member,
                g.{geo_name_col} AS country,
                COUNT(*) OVER (PARTITION BY g.{geo_name_col}) AS country_members
              FROM {FQN}.MEMBER_ITG m
              JOIN {FQN}.GEOGRAPHY g ON m.{country_col} = g.{geo_country_col}
             WHERE {_active_filter(member_cols)}
             ORDER BY country_members DESC, member
             LIMIT 10
            """,
        )
        if not partners.empty:
            partners = partners.rename(
                columns={"MEMBER": "Member", "COUNTRY": "Country", "COUNTRY_MEMBERS": "country_members"}
            )
            partners["Volume"] = partners["country_members"].apply(lambda n: f"{int(n)} members")
            partners["Growth"] = "—"
            partners["positive"] = True
            partners = partners[["Member", "Country", "Volume", "Growth", "positive"]]

    return DashboardData(
        source="snowflake",
        last_updated=last_updated,
        overview_cards=overview_cards,
        region_chart=region_chart,
        country_chart=country_chart,
        partners=partners,
    )


def load_demo_data() -> DashboardData:
    return DashboardData(
        source="demo",
        last_updated=datetime.now(timezone.utc).strftime("Today, %I:%M %p UTC"),
        overview_cards=[
            {"label": "Net Sales", "value": "€3.2M", "delta": "+10%", "positive": True},
            {"label": "Net Sales", "value": "€3.2M", "delta": "+10%", "positive": True},
            {"label": "Net Sales", "value": "€3.2M", "delta": "-5%", "positive": False},
            {"label": "Net Sales", "value": "€3.2M", "delta": "+10%", "positive": True},
        ],
        region_chart=pd.DataFrame(
            {"region": [str(y) for y in range(2016, 2024)], "member_count": [18, 22, 28, 35, 42, 55, 72, 88]}
        ),
        country_chart=pd.DataFrame(
            {
                "country": ["NY", "MA", "NH", "OR"],
                "member_count": [120, 95, 80, 65],
            }
        ),
        partners=pd.DataFrame(
            {
                "Member": ["Digitalisim", "Digitalisim", "Digitalisim"],
                "Country": ["France", "France", "France"],
                "Volume": ["€100K", "€100K", "€100K"],
                "Growth": ["+10%", "-10%", "+10%"],
                "positive": [True, False, True],
            }
        ),
    )
