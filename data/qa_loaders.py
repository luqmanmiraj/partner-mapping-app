"""QA views — overlap and discrepancy data (demo + optional Snowflake)."""

from __future__ import annotations

import pandas as pd


def load_overlap_cases(conn=None) -> pd.DataFrame:
    """Parent vs descendant overlap cases — QA.V_DOUBLE_COUNTING_CHECK or demo."""
    if conn is not None:
        from auth.snowflake_session import schema_fqn
        from snowflake_client import query_df

        try:
            return query_df(
                conn,
                f"""
                SELECT case_id AS "Case ID",
                       period AS "Period",
                       supplier AS "Supplier",
                       parent_declarant AS "Parent",
                       parent_amount AS "Parent Amount",
                       descendants_sum AS "Descendants Sum",
                       gap_eur AS "Gap (EUR)",
                       gap_pct || '%' AS "Gap (%)",
                       status AS "Status"
                FROM {schema_fqn("QA")}.V_DOUBLE_COUNTING_CHECK
                ORDER BY gap_pct DESC
                LIMIT 100
                """,
            )
        except Exception:
            pass

    from data.demo_fixtures import overlap_cases

    return overlap_cases()


def load_discrepancy_matrix(conn=None) -> pd.DataFrame:
    """Supplier vs member turnover discrepancies — QA.DECLARATION_DISCREPANCY or demo."""
    if conn is not None:
        from auth.snowflake_session import schema_fqn
        from snowflake_client import query_df

        try:
            df = query_df(
                conn,
                f"""
                SELECT supplier AS "Supplier",
                       member AS "Member",
                       turnover_supplier AS "Turnover (Supplier)",
                       turnover_member AS "Turnover (Member)",
                       abs_gap AS "Abs. Gap",
                       rel_gap AS "Rel. Gap",
                       tag AS "Tag"
                FROM {schema_fqn("QA")}.DECLARATION_DISCREPANCY
                ORDER BY abs_gap DESC
                LIMIT 100
                """,
            )
            if not df.empty:
                df["Pair"] = df["Supplier"].astype(str) + " / " + df["Member"].astype(str)
            return df
        except Exception:
            pass

    from data.demo_fixtures import discrepancy_matrix

    df = discrepancy_matrix().copy()
    df["Pair"] = df["Supplier"].astype(str) + " / " + df["Member"].astype(str)
    return df
