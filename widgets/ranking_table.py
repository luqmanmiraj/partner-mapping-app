"""Ranked entity table with growth badges."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.html_utils import render_html


def render_ranking_table(policy: HubDashboardPolicy, df: pd.DataFrame) -> None:
    if df.empty:
        st.info("No rows available.")
        return

    entity_col = policy.ranking_entity_key
    cols = list(policy.ranking_columns)
    header = "".join(f"<th>{html.escape(c)}</th>" for c in cols)

    rows = ""
    for _, row in df.iterrows():
        entity = row.get(entity_col, row.get(entity_col.upper(), ""))
        country = row.get("Country", row.get("COUNTRY", ""))
        volume = row.get("Volume", row.get("VOLUME", ""))
        growth = row.get("Growth", row.get("GROWTH", ""))
        positive = bool(row.get("positive", row.get("POSITIVE", True)))
        badge_class = "positive" if positive else "negative"
        arrow = "↗" if positive else "↘"
        rows += f"""
        <tr>
            <td>{html.escape(str(entity))}</td>
            <td>{html.escape(str(country))}</td>
            <td>{html.escape(str(volume))}</td>
            <td><span class="delta-badge {badge_class}">{arrow} {html.escape(str(growth))}</span></td>
        </tr>
        """

    render_html(
        f"""
        <div class="card" style="padding:0;overflow:hidden;">
            <table class="partners-table">
                <thead><tr>{header}</tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """
    )
