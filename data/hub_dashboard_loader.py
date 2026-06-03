"""Load hub dashboard data and apply content policy labels."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from content_policies.hub_dashboard import HubDashboardPolicy, get_hub_dashboard_policy
from dashboard_data import DashboardData, load_demo_data, load_from_snowflake
from auth.session import UserSession, get_session


@dataclass
class HubDashboardViewModel:
    policy: HubDashboardPolicy
    last_updated: str
    overview_cards: list[dict]
    region_chart: pd.DataFrame
    country_chart: pd.DataFrame
    ranking_table: pd.DataFrame
    source: str = "demo"


def _apply_policy_to_cards(cards: list[dict], policy: HubDashboardPolicy) -> list[dict]:
    if policy.kpi_primary_label == "Net Sales":
        return cards
    return [
        {**card, "label": policy.kpi_primary_label if card.get("label") == "Net Sales" else card["label"]}
        for card in cards
    ]


def _apply_policy_to_ranking(df: pd.DataFrame, policy: HubDashboardPolicy) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if policy.ranking_entity_key != "Member" and "Member" in out.columns:
        out = out.rename(columns={"Member": policy.ranking_entity_key})
    elif policy.ranking_entity_key != "Member" and "MEMBER" in out.columns:
        out = out.rename(columns={"MEMBER": policy.ranking_entity_key})
    return out


def _chart_titles_for_snowflake(policy: HubDashboardPolicy, source: str) -> HubDashboardPolicy:
    """Snowflake REF data uses member geography — adjust chart titles only when live."""
    if source != "snowflake":
        return policy
    from dataclasses import replace

    if policy.declarant_type == "supplier":
        return replace(
            policy,
            chart_left_title="Members by Region",
            chart_right_title="Members by Country",
        )
    return replace(
        policy,
        chart_left_title="Suppliers by Region",
        chart_right_title="Suppliers by Country",
    )


def load_hub_dashboard(
    session: UserSession | None = None,
    conn=None,
) -> HubDashboardViewModel:
    session = session or get_session()
    policy = get_hub_dashboard_policy(session)

    if conn is not None:
        raw = load_from_snowflake(conn)
        policy = _chart_titles_for_snowflake(policy, raw.source)
        return HubDashboardViewModel(
            policy=policy,
            last_updated=raw.last_updated,
            overview_cards=_apply_policy_to_cards(raw.overview_cards, policy),
            region_chart=raw.region_chart,
            country_chart=raw.country_chart,
            ranking_table=_apply_policy_to_ranking(raw.partners, policy),
            source=raw.source,
        )

    raw = load_demo_data()
    ranking = raw.partners.copy()
    if policy.declarant_type == "member" and "Member" in ranking.columns:
        ranking = ranking.rename(columns={"Member": "Supplier"})

    return HubDashboardViewModel(
        policy=policy,
        last_updated=raw.last_updated,
        overview_cards=_apply_policy_to_cards(raw.overview_cards, policy),
        region_chart=raw.region_chart,
        country_chart=raw.country_chart,
        ranking_table=_apply_policy_to_ranking(ranking, policy),
        source=raw.source,
    )
