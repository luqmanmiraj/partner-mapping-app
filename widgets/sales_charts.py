"""Sales charts widget — area + horizontal bar."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.tokens import BORDER, ORANGE, TEXT_MUTED, TEXT_PRIMARY


def _series(df: pd.DataFrame, *column_candidates: str) -> pd.Series:
    for col in column_candidates:
        if col in df.columns:
            return df[col]
        upper = col.upper()
        if upper in df.columns:
            return df[upper]
    raise KeyError(f"None of {column_candidates} found in {list(df.columns)}")


def build_area_chart(df: pd.DataFrame, *, title: str) -> go.Figure:
    x = _series(df, "region", "REGION", "period", "PERIOD")
    y = _series(df, "member_count", "MEMBER_COUNT", "value", "VALUE")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=ORANGE, width=2, dash="dot"),
            fill="tozeroy",
            fillcolor="rgba(245, 130, 32, 0.18)",
            hovertemplate="%{x}: %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=TEXT_PRIMARY)),
        margin=dict(l=10, r=10, t=40, b=30),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color=TEXT_MUTED), linecolor=BORDER),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=11, color=TEXT_MUTED), linecolor=BORDER),
        showlegend=False,
        hovermode="x unified",
    )
    return fig


def build_bar_chart(df: pd.DataFrame, *, title: str) -> go.Figure:
    labels = _series(df, "country", "COUNTRY", "label", "LABEL").astype(str)
    values = _series(df, "member_count", "MEMBER_COUNT", "value", "VALUE").astype(float)
    fig = go.Figure(
        go.Bar(
            y=labels,
            x=values,
            orientation="h",
            marker=dict(color=values, colorscale=[[0, "#FDEAD7"], [1, ORANGE]], line=dict(width=0)),
            text=[str(int(v)) for v in values],
            textposition="outside",
            textfont=dict(size=11, color=TEXT_PRIMARY),
            hovertemplate="%{y}: %{x}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=TEXT_PRIMARY)),
        margin=dict(l=10, r=40, t=40, b=10),
        height=300,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color=TEXT_PRIMARY), autorange="reversed"),
        showlegend=False,
    )
    return fig


def render_sales_charts(
    policy: HubDashboardPolicy,
    region_chart: pd.DataFrame,
    country_chart: pd.DataFrame,
    *,
    column_weights: tuple[int | float, int | float] | None = None,
) -> None:
    if column_weights:
        col_left, col_right = st.columns(column_weights, gap="medium")
    else:
        col_left, col_right = st.columns(2, gap="medium")
    with col_left:
        if not region_chart.empty:
            st.plotly_chart(
                build_area_chart(region_chart, title=policy.chart_left_title),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.info("No chart data available.")
    with col_right:
        if not country_chart.empty:
            st.plotly_chart(
                build_bar_chart(country_chart, title=policy.chart_right_title),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.info("No chart data available.")
