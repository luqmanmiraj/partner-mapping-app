"""KPI metric cards row widget."""

from __future__ import annotations

import html

from theme.html_utils import render_html


def render_kpi_overview(cards: list[dict]) -> None:
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
