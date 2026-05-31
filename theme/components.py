"""Reusable UI components for NEXUS Streamlit pages."""

from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from theme.html_utils import render_html
from theme.tokens import STATUS_COLORS, TEXT_MUTED


def render_page_header(display_name: str, *, subtitle: str = "") -> None:
    """Page header with welcome text, notification bell, and profile chip."""
    from widgets.notifications_panel import render_notification_bell

    title_col, bell_col, profile_col = st.columns([8.5, 0.75, 0.75])
    with title_col:
        st.markdown(f"# Welcome {html.escape(display_name)},")
        if subtitle:
            st.caption(subtitle)
    with bell_col:
        render_notification_bell()
    with profile_col:
        st.markdown("👤 ▾")


def render_section_header(title: str, *, subtitle: str = "") -> None:
    sub = f'<div class="subtitle">{html.escape(subtitle)}</div>' if subtitle else ""
    render_html(
        f"""
        <div class="section-header">
            <div>
                <h2>{html.escape(title)}</h2>
                {sub}
            </div>
        </div>
        """
    )


def render_metric_cards(cards: list[dict]) -> None:
    cards_html = ""
    for card in cards:
        badge_class = "positive" if card.get("positive", True) else "negative"
        arrow = "↗" if card.get("positive", True) else "↘"
        cards_html += f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(card["label"]))}</div>
            <div class="metric-value">{html.escape(str(card["value"]))}</div>
            <span class="delta-badge {badge_class}">{arrow} {html.escape(str(card.get("delta", "")))}</span>
        </div>
        """
    render_html(f'<div class="metric-grid">{cards_html}</div>')


def status_badge_html(status: str) -> str:
    fg, bg = STATUS_COLORS.get(status, (TEXT_MUTED, "#F3F4F6"))
    return (
        f'<span class="status-badge" style="background:{bg};color:{fg};">'
        f"{html.escape(status)}</span>"
    )


def render_data_table(df: pd.DataFrame, *, columns: list[str] | None = None) -> None:
    if df.empty:
        render_html('<div class="empty-state">No data available.</div>')
        return
    cols = columns or list(df.columns)
    header = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    rows = ""
    for _, row in df.iterrows():
        cells = ""
        for c in cols:
            val = row.get(c, "")
            if c == "Status" and val in STATUS_COLORS:
                cells += f"<td>{status_badge_html(str(val))}</td>"
            else:
                cells += f"<td>{html.escape(str(val))}</td>"
        rows += f"<tr>{cells}</tr>"
    render_html(
        f"""
        <div class="card" style="padding:0;overflow:hidden;">
            <table class="data-table">
                <thead><tr>{header}</tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """
    )


def render_warning_banner(message: str) -> None:
    render_html(f'<div class="warning-banner">⚠ {html.escape(message)}</div>')


def render_empty_state(title: str, message: str) -> None:
    render_html(
        f"""
        <div class="card empty-state">
            <h3 style="margin:0 0 0.5rem 0;">{html.escape(title)}</h3>
            <p style="margin:0;">{html.escape(message)}</p>
        </div>
        """
    )
