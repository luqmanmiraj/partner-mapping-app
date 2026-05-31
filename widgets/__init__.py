"""Shared dashboard widgets — same layout/styling, data from content policies."""

from widgets.hero_banner import render_hero_banner
from widgets.kpi_overview import render_kpi_overview
from widgets.ranking_table import render_ranking_table
from widgets.sales_charts import render_sales_charts
from widgets.section_toolbar import render_section_toolbar
from widgets.upcoming_features import render_upcoming_features
from widgets.notifications_panel import open_notifications_dialog, render_notification_bell

__all__ = [
    "render_hero_banner",
    "render_upcoming_features",
    "render_section_toolbar",
    "render_kpi_overview",
    "render_sales_charts",
    "render_ranking_table",
    "open_notifications_dialog",
    "render_notification_bell",
]
