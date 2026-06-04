"""Hub portal dashboard — composes shared widgets + role content policy."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from data.hub_dashboard_loader import load_hub_dashboard
from theme.components import render_page_header
from theme.html_utils import inject_parent_styles
from theme.member_templates import (
    render_member_dashboard_overview,
    render_member_dashboard_ranking,
    render_member_dashboard_sales_header,
)
from widgets.hero_banner import render_hero_banner
from widgets.overview_section import render_overview_section
from widgets.ranking_table import render_ranking_table
from widgets.sales_charts import render_sales_charts
from widgets.section_toolbar import render_section_toolbar
from widgets.upcoming_features import render_upcoming_features

_MEMBER_DASHBOARD_SCOPE = '[data-testid="stMain"] .st-key-member_dashboard_page'
_MEMBER_DASHBOARD_SALES_SCOPE = '[data-testid="stMain"] .st-key-member_dashboard_sales_charts'
_MEMBER_DASHBOARD_STYLE_ID = "member-dashboard-page"


def _inject_member_dashboard_page_styles() -> None:
    """Streamlit page CSS — full-width st.html block for member dashboard."""
    inject_parent_styles(
        f"""
        {_MEMBER_DASHBOARD_SCOPE} {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }}

        {_MEMBER_DASHBOARD_SCOPE} [data-testid="stHtml"],
        {_MEMBER_DASHBOARD_SCOPE} [data-testid="stHtml"] iframe {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {_MEMBER_DASHBOARD_SALES_SCOPE} {{
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            margin-top: -8px;
        }}

        {_MEMBER_DASHBOARD_SALES_SCOPE} [data-testid="column"] {{
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}

        {_MEMBER_DASHBOARD_SALES_SCOPE} [data-testid="stHorizontalBlock"] {{
            gap: 24px !important;
        }}

        {_MEMBER_DASHBOARD_SALES_SCOPE} [data-testid="stPlotlyChart"] {{
            background: #ffffff;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        }}
        """,
        style_id=_MEMBER_DASHBOARD_STYLE_ID,
    )


def render(active_page: str = "hub_dashboard") -> None:
    session = get_session()
    # For member persona, use the static HTML prototype so the dashboard
    # matches the member design exactly.
    if getattr(session, "declarant_type", "") == "member":
        use_sf = st.session_state.get("use_snowflake", False)
        passcode = st.session_state.get("passcode", "")

        with scoped_connection(passcode, force_demo=not use_sf) as conn:
            vm = load_hub_dashboard(session, conn)

        _inject_member_dashboard_page_styles()
        with st.container(key="member_dashboard_page"):
            render_member_dashboard_overview()
            render_member_dashboard_sales_header(vm.policy.sales_title, vm.last_updated)
            with st.container(key="member_dashboard_sales_charts"):
                render_sales_charts(
                    vm.policy,
                    vm.region_chart,
                    vm.country_chart,
                    column_weights=(2, 1),
                )
            render_member_dashboard_ranking()

        if vm.source == "demo":
            st.caption(f"Demo data · Policy: {vm.policy.role_key} ({vm.policy.declarant_type})")
        return

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        vm = load_hub_dashboard(session, conn)

    policy = vm.policy

    if "hero" in policy.visible_sections:
        render_hero_banner(policy)

    render_page_header(session.display_name)

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
