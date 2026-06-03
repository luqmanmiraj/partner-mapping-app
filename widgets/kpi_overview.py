"""KPI metric cards row widget (legacy global classes)."""

from __future__ import annotations

from theme.components import render_metric_cards


def render_kpi_overview(cards: list[dict]) -> None:
    """Render KPI cards only — prefer render_overview_section on the hub dashboard."""
    render_metric_cards(cards)
