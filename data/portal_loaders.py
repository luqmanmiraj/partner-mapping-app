"""Hub portal data loaders from Snowflake REF schema."""

from __future__ import annotations

import streamlit as st

import pandas as pd

from auth.snowflake_session import schema_fqn
from snowflake_client import pick_column, query_df, table_columns

FQN = schema_fqn("REF")


def _active_member_filter(member_cols: dict[str, str]) -> str:
    if "leave_date" in member_cols:
        return f"{member_cols['leave_date']} IS NULL"
    return "1=1"


def load_member_directory(conn) -> list[dict]:
    member_cols = table_columns(conn, "MEMBER_ITG")
    geo_cols = table_columns(conn, "GEOGRAPHY")
    name_col = pick_column(member_cols, "company_name", "member_name", "company_path", "name")
    id_col = pick_column(member_cols, "id_code", "member_id", "id")
    country_col = pick_column(
        member_cols, "country_code", "iso_country_code", "country_iso_code", "iso_code", "country"
    )
    level_col = pick_column(member_cols, "hierarchylevel", "hierarchy_level", "level")
    geo_country_col = pick_column(geo_cols, "country_code", "iso_code", "iso_country_code")
    geo_name_col = pick_column(geo_cols, "country_name", "name")

    if not name_col:
        return []

    join = ""
    country_select = "NULL AS country_name"
    if country_col and geo_country_col and geo_name_col:
        join = f"LEFT JOIN {FQN}.GEOGRAPHY g ON m.{country_col} = g.{geo_country_col}"
        country_select = f"g.{geo_name_col} AS country_name"

    sql = f"""
        SELECT m.{name_col} AS company_name, {country_select},
               {f'm.{id_col}' if id_col else "NULL"} AS id_code,
               {f'm.{level_col}' if level_col else "NULL"} AS hierarchylevel
        FROM {FQN}.MEMBER_ITG m
        {join}
        WHERE {_active_member_filter(member_cols)}
        ORDER BY company_name
        LIMIT 200
    """
    try:
        df = query_df(conn, sql)
    except Exception as exc:
        st.session_state.snowflake_error = f"Member directory query failed: {exc}"
        return []

    companies = []
    for _, row in df.iterrows():
        companies.append(
            {
                "name": str(row.get("COMPANY_NAME", row.get("company_name", ""))),
                "country": str(row.get("COUNTRY_NAME", row.get("country_name", ""))),
                "code": str(row.get("ID_CODE", row.get("id_code", ""))),
                "level": str(row.get("HIERARCHYLEVEL", row.get("hierarchylevel", ""))),
            }
        )
    return companies


def load_my_company(conn, partner_key: str, declarant_type: str) -> dict:
    decl_cols = table_columns(conn, "DECLARANT_PARTNER")
    key_col = pick_column(decl_cols, "partner_key", "declarant_key", "partner_id") or "partner_key"
    type_col = pick_column(decl_cols, "declarant_type", "type")
    currency_col = pick_column(decl_cols, "default_currency", "currency_code", "currency")
    active_col = pick_column(decl_cols, "is_active", "active")

    safe_key = partner_key.replace("'", "''")
    sql = f"""
        SELECT * FROM {FQN}.DECLARANT_PARTNER
        WHERE {key_col} = '{safe_key}'
        LIMIT 1
    """
    try:
        df = query_df(conn, sql)
    except Exception as exc:
        st.session_state.snowflake_error = f"My Company query failed: {exc}"
        return {}

    if df.empty:
        return {}
    row = df.iloc[0]
    name = partner_key.replace("_", " ")
    return {
        "name": name,
        "type": str(row.get(type_col.upper() if type_col else "", declarant_type)) if type_col else declarant_type,
        "currency": str(row.get(currency_col.upper() if currency_col else "", "EUR")) if currency_col else "EUR",
        "is_active": bool(row.get(active_col.upper() if active_col else "", True)) if active_col else True,
        "tagline": f"{name} — NEXUS partner profile",
    }


def load_supplier_portfolio(conn) -> pd.DataFrame:
    sup_cols = table_columns(conn, "SUPPLIER")
    brand_cols = table_columns(conn, "BRAND")
    id_col = pick_column(sup_cols, "supplier_id", "id")
    name_col = pick_column(sup_cols, "supplier_name", "name", "company_name")
    brand_col = pick_column(brand_cols, "brand_name", "name")
    brand_sup_col = pick_column(brand_cols, "supplier_id", "id")

    if not name_col:
        return pd.DataFrame()

    join = ""
    brand_select = "NULL AS brand_name"
    if brand_col and brand_sup_col and id_col:
        join = f"LEFT JOIN {FQN}.BRAND b ON s.{id_col} = b.{brand_sup_col}"
        brand_select = f"b.{brand_col} AS brand_name"

    leave_filter = "1=1"
    if "leave_date" in sup_cols:
        leave_filter = f"s.{sup_cols['leave_date']} IS NULL"

    sql = f"""
        SELECT s.{id_col or 'supplier_id'} AS supplier_id,
               s.{name_col} AS supplier_name,
               {brand_select}
        FROM {FQN}.SUPPLIER s
        {join}
        WHERE {leave_filter}
        ORDER BY supplier_name
        LIMIT 100
    """
    try:
        return query_df(conn, sql)
    except Exception as exc:
        st.session_state.snowflake_error = f"Supplier portfolio query failed: {exc}"
        return pd.DataFrame()
