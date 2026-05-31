"""Role-based content policies for hub portal widgets."""

from __future__ import annotations

from dataclasses import dataclass, field

from auth.session import UserSession, get_session


@dataclass(frozen=True)
class HubDashboardPolicy:
    """Labels and visibility rules — shared widgets, role-specific content."""

    role_key: str
    declarant_type: str

    # Section titles
    overview_title: str = "Overview"
    sales_title: str = "Sales"
    ranking_title: str = "Top Performing Partners"

    # Chart labels
    chart_left_title: str = "Sales by Country"
    chart_right_title: str = "Sales by Product Group"

    # Ranking table columns (display headers)
    ranking_columns: tuple[str, ...] = ("Member", "Country", "Volume", "Growth")
    ranking_entity_key: str = "Member"

    # Hero copy
    hero_headline: str = "Welcome to your centralized hub."
    hero_bullets: tuple[str, ...] = (
        "Drive your performance",
        "Access exclusive deals",
        "And stay connected with the global Nexus ecosystem",
    )

    # Feature blurb
    upcoming_blurb: str = (
        "Soon you will be able to discover supplier books, key performances, "
        "and data analysis — all in one place to help you make smarter decisions."
    )

    # Toolbar filters shown on overview
    show_import_export: bool = True
    filter_labels: tuple[str, ...] = ("Date", "Product group")

    # KPI card label template (demo / snowflake may override values)
    kpi_primary_label: str = "Net Sales"

    visible_sections: tuple[str, ...] = (
        "hero",
        "upcoming_features",
        "overview",
        "sales",
        "ranking",
    )


def _supplier_policy() -> HubDashboardPolicy:
    return HubDashboardPolicy(
        role_key="supplier",
        declarant_type="supplier",
        ranking_title="Top Performing Partners",
        ranking_columns=("Member", "Country", "Volume", "Growth"),
        ranking_entity_key="Member",
        chart_left_title="Sales by Country",
        chart_right_title="Sales by Product Group",
        upcoming_blurb=(
            "Soon you will be able to discover supplier books, key performances, "
            "and data analysis — all in one place to help you make smarter decisions."
        ),
        filter_labels=("Date", "Product group"),
    )


def _member_policy() -> HubDashboardPolicy:
    return HubDashboardPolicy(
        role_key="member",
        declarant_type="member",
        ranking_title="Top Performing Suppliers",
        ranking_columns=("Supplier", "Country", "Volume", "Growth"),
        ranking_entity_key="Supplier",
        chart_left_title="Purchases by Region",
        chart_right_title="Purchases by Category",
        upcoming_blurb=(
            "Soon you will be able to explore supplier performance, exclusive deals, "
            "and network analytics — all in one place to support your business."
        ),
        filter_labels=("Date", "Category"),
        kpi_primary_label="Net Purchases",
    )


def _reviewer_policy() -> HubDashboardPolicy:
    return HubDashboardPolicy(
        role_key="reviewer",
        declarant_type="internal",
        ranking_title="Top Network Partners",
        ranking_columns=("Partner", "Country", "Volume", "Growth"),
        ranking_entity_key="Partner",
        chart_left_title="Network turnover by region",
        chart_right_title="Turnover by product group",
        show_import_export=True,
        filter_labels=("Date", "Partner type"),
        kpi_primary_label="Network turnover",
        upcoming_blurb=(
            "Internal cockpit widgets reuse the same layout as partner dashboards "
            "with aggregated, cross-partner metrics."
        ),
    )


def get_hub_dashboard_policy(session: UserSession | None = None) -> HubDashboardPolicy:
    session = session or get_session()
    if session.role_type == "reviewer" or session.role_type == "admin":
        return _reviewer_policy()
    if session.declarant_type == "member":
        return _member_policy()
    return _supplier_policy()
