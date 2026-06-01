"""Shared dashboard widgets — same layout/styling, data from content policies."""

from widgets.hero_banner import render_hero_banner
from widgets.kpi_overview import render_kpi_overview
from widgets.overview_section import render_overview_section
from widgets.ranking_table import render_ranking_table
from widgets.sales_charts import render_sales_charts
from widgets.section_toolbar import render_section_toolbar
from widgets.upcoming_features import render_upcoming_features
from widgets.notifications_dropdown import build_notifications_dropdown_html
from widgets.notifications_panel import open_notifications_dialog, render_notification_bell
from widgets.user_dropdown import build_user_dropdown_html

__all__ = [
    "render_hero_banner",
    "render_upcoming_features",
    "render_section_toolbar",
    "render_kpi_overview",
    "render_overview_section",
    "render_sales_charts",
    "render_ranking_table",
    "build_notifications_dropdown_html",
    "build_user_dropdown_html",
    "open_notifications_dialog",
    "render_notification_bell",
]
