"""Hub portal dashboard — composes shared widgets + role content policy."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from data.hub_dashboard_loader import load_hub_dashboard
from theme.components import render_page_header
from widgets.hero_banner import render_hero_banner
from widgets.overview_section import render_overview_section
from widgets.ranking_table import render_ranking_table
from widgets.sales_charts import render_sales_charts
from widgets.section_toolbar import render_section_toolbar
from widgets.upcoming_features import render_upcoming_features


def render(active_page: str = "hub_dashboard") -> None:
    session = get_session()
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        vm = load_hub_dashboard(session, conn)

    policy = vm.policy
    render_page_header(session.display_name)

    if "hero" in policy.visible_sections:
        render_hero_banner(policy)

    if "upcoming_features" in policy.visible_sections:
        render_upcoming_features(policy)

    if "overview" in policy.visible_sections:
        render_overview_section(policy, vm.last_updated, vm.overview_cards)

    if "sales" in policy.visible_sections:
        render_section_toolbar(policy.sales_title, vm.last_updated, policy=policy)
        render_sales_charts(policy, vm.region_chart, vm.country_chart)

    if "ranking" in policy.visible_sections:
        render_section_toolbar(policy.ranking_title, vm.last_updated, policy=policy)
        render_ranking_table(policy, vm.ranking_table)

    if vm.source == "demo":
        st.caption(f"Demo data · Policy: {policy.role_key} ({policy.declarant_type})")
