"""Partner — Financial dashboard (BRD turnover view)."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from data.dashboard_metrics import load_financial_dashboard
from theme.components import render_data_table, render_metric_cards, render_page_header, render_section_header
from theme.tokens import BORDER, ORANGE, TEXT_MUTED, TEXT_PRIMARY
from widgets.workflow_logs_section import render_workflow_logs_controls


def _build_turnover_chart(monthly, *, granularity: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=monthly["period"],
            y=monthly["turnover_eur"],
            name="Current (EUR)",
            mode="lines+markers",
            line=dict(color=ORANGE, width=2),
            fill="tozeroy",
            fillcolor="rgba(245, 130, 32, 0.15)",
        )
    )
    if "turnover_n1" in monthly.columns:
        fig.add_trace(
            go.Scatter(
                x=monthly["period"],
                y=monthly["turnover_n1"],
                name="N-1 (EUR)",
                mode="lines",
                line=dict(color=TEXT_MUTED, width=2, dash="dot"),
            )
        )
    fig.update_layout(
        title=dict(text=f"Turnover — {granularity.title()}", x=0, font=dict(size=15)),
        margin=dict(l=10, r=10, t=40, b=30),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, linecolor=BORDER),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", linecolor=BORDER),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified",
    )
    return fig


def render(active_page: str = "dashboard") -> None:
    session = get_session()
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    render_page_header(session.display_name, subtitle="Financial dashboard")

    render_workflow_logs_controls(
        partner_key=session.partner_key,
        button_key="financial_logs_view_btn",
        session_flag="show_workflow_logs_financial",
        strip_key="financial_workflow_logs_strip",
        title="Workflow activity log",
    )

    granularity = st.radio(
        "View",
        ["monthly", "quarterly"],
        horizontal=True,
        format_func=lambda x: x.title(),
    )

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        data = load_financial_dashboard(session, conn, granularity=granularity)

    source_label = "Snowflake" if data.get("source") == "snowflake" else "Demo data"
    render_section_header("Overview", subtitle=f"Last updated: {data['last_updated']} ({source_label})")

    render_metric_cards(data["overview_cards"])

    col1, col2 = st.columns([3, 2])
    with col1:
        monthly = data["monthly"]
        if not monthly.empty:
            st.plotly_chart(
                _build_turnover_chart(monthly, granularity=granularity),
                use_container_width=True,
                config={"displayModeBar": False},
            )

    with col2:
        render_section_header(f"Top 10 {session.counterparty_label}", subtitle="Amounts in EUR")
        render_data_table(data["top_counterparties"])

    if data.get("period_closed"):
        st.warning("One or more selected periods are closed. Figures are frozen for accounting.")
