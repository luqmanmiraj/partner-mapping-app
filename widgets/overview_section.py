"""Overview dashboard section — matches .prototype/sections/overview.html."""

from __future__ import annotations

import html

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.html_utils import render_html

_ROOT = "nexus-overview"

_CHEVRON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23444' stroke-width='2' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'"
    "%3e%3c/polyline%3e%3c/svg%3e"
)
_IMPORT_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23111' stroke-width='2.5' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3e"
    "%3cpolyline points='7 10 12 15 17 10'/%3e%3cline x1='12' y1='15' x2='12' y2='3'/%3e%3c/svg%3e"
)
_EXPORT_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23111' stroke-width='2.5' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3e"
    "%3cpolyline points='17 8 12 3 7 8'/%3e%3cline x1='12' y1='3' x2='12' y2='15'/%3e%3c/svg%3e"
)
_TREND_UP = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23219653' stroke-width='3' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='23 6 13.5 15.5 8.5 10.5 1 18'/%3e"
    "%3cpolyline points='17 6 23 6 23 12'/%3e%3c/svg%3e"
)
_TREND_DOWN = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23eb5757' stroke-width='3' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='23 18 13.5 8.5 8.5 13.5 1 6'/%3e"
    "%3cpolyline points='17 18 23 18 23 12'/%3e%3c/svg%3e"
)


def overview_section_styles() -> str:
    """Prototype CSS scoped under .nexus-overview (avoids global .metric-card rules)."""
    r = _ROOT
    return f"""
        section.main [data-testid="stHtml"]:has(.{r}) {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        .{r} {{
            --text-main: #111111;
            --text-muted: #666666;
            --border-color: #cccccc;
            --card-label-orange: #d97706;
            --green-badge-bg: #e2f6ec;
            --green-badge-text: #219653;
            --red-badge-bg: #fde8e8;
            --red-badge-text: #eb5757;
            width: 100%;
            max-width: none;
            margin-bottom: 1rem;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        .{r} .overview-section {{
            width: 100%;
            max-width: none;
            display: flex;
            flex-direction: column;
            gap: 16px;
            box-sizing: border-box;
        }}

        .{r} .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }}

        .{r} .title-area {{
            display: flex;
            align-items: baseline;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .{r} .title-area h2 {{
            font-size: 22px;
            font-weight: 700;
            color: var(--text-main);
            margin: 0;
            line-height: 1.2;
        }}

        .{r} .timestamp {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        .{r} .controls-toolbar {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .{r} .select-menu {{
            padding: 8px 36px 8px 14px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: #ffffff;
            font-size: 13px;
            color: #444444;
            cursor: pointer;
            appearance: none;
            -webkit-appearance: none;
            background-image: url("{_CHEVRON}");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 12px;
            min-width: 140px;
            line-height: 1.3;
        }}

        .{r} .action-btn {{
            background-color: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 14px 8px 34px;
            font-size: 13px;
            font-weight: 500;
            color: var(--text-main);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background-color 0.15s ease;
            position: relative;
            line-height: 1.3;
        }}

        .{r} .action-btn:hover {{
            background-color: #f9f9f9;
        }}

        .{r} .action-btn__icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 14px;
            height: 14px;
            background: center / contain no-repeat;
            flex-shrink: 0;
        }}

        .{r} .action-btn__icon--import {{
            background-image: url("{_IMPORT_ICON}");
        }}

        .{r} .action-btn__icon--export {{
            background-image: url("{_EXPORT_ICON}");
        }}

        .{r} .cards-viewport-wrapper {{
            background: linear-gradient(to right, #fff4eb, #fdf8f4) !important;
            padding: 24px;
            border-radius: 8px;
            box-sizing: border-box;
            width: 100%;
            max-width: none;
        }}

        .{r} .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
        }}

        .{r} .metric-card {{
            background-color: #ffffff !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 20px !important;
            display: flex;
            flex-direction: column;
            gap: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.01);
            margin: 0 !important;
        }}

        .{r} .card-title {{
            color: var(--card-label-orange) !important;
            font-size: 13px;
            font-weight: 700;
            text-transform: capitalize;
            margin: 0 !important;
        }}

        .{r} .card-value {{
            font-size: 28px;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.5px;
            line-height: 1.1;
            margin: 0 !important;
        }}

        .{r} .status-badge {{
            align-self: flex-start;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .{r} .status-badge__trend {{
            width: 10px;
            height: 10px;
            background: center / contain no-repeat;
            flex-shrink: 0;
        }}

        .{r} .status-badge__trend--up {{
            background-image: url("{_TREND_UP}");
        }}

        .{r} .status-badge__trend--down {{
            background-image: url("{_TREND_DOWN}");
        }}

        .{r} .badge-up {{
            background-color: var(--green-badge-bg);
            color: var(--green-badge-text);
        }}

        .{r} .badge-down {{
            background-color: var(--red-badge-bg);
            color: var(--red-badge-text);
        }}

        @media (max-width: 992px) {{
            .{r} .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 576px) {{
            .{r} .metrics-grid {{
                grid-template-columns: 1fr;
            }}
            .{r} .section-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .{r} .controls-toolbar {{
                width: 100%;
            }}
            .{r} .select-menu,
            .{r} .action-btn {{
                flex-grow: 1;
            }}
        }}
    """


def inject_overview_section_styles() -> None:
    """Register overview CSS with app startup (same pattern as top header / sidenav)."""
    render_html(f"<style>{overview_section_styles()}</style>")


def _controls_html(policy: HubDashboardPolicy) -> str:
    f1 = html.escape(policy.filter_labels[0])
    f2 = html.escape(
        policy.filter_labels[1] if len(policy.filter_labels) > 1 else "Filter"
    )
    return f"""
            <div class="controls-toolbar">
                <select class="select-menu" aria-label="Filter by Date">
                    <option selected>{f1}</option>
                    <option>Last 7 days</option>
                    <option>Last 30 days</option>
                    <option>YTD</option>
                </select>
                <select class="select-menu" aria-label="Filter by Type">
                    <option selected>{f2}</option>
                    <option>All regions</option>
                    <option>All products</option>
                </select>
                <button type="button" class="action-btn">
                    <span class="action-btn__icon action-btn__icon--import" aria-hidden="true"></span>
                    Import
                </button>
                <button type="button" class="action-btn">
                    <span class="action-btn__icon action-btn__icon--export" aria-hidden="true"></span>
                    Export
                </button>
            </div>
    """


def _metric_cards_html(cards: list[dict]) -> str:
    blocks = ""
    for card in cards:
        positive = card.get("positive", True)
        badge = "badge-up" if positive else "badge-down"
        trend = "status-badge__trend--up" if positive else "status-badge__trend--down"
        delta = html.escape(str(card.get("delta", "")))
        blocks += f"""
                <div class="metric-card">
                    <span class="card-title">{html.escape(str(card["label"]))}</span>
                    <span class="card-value">{html.escape(str(card["value"]))}</span>
                    <span class="status-badge {badge}">
                        <span class="status-badge__trend {trend}" aria-hidden="true"></span>
                        {delta}
                    </span>
                </div>
        """
    return blocks


def build_overview_html(
    policy: HubDashboardPolicy,
    last_updated: str,
    cards: list[dict],
) -> str:
    """Full overview section markup (prototype structure)."""
    r = _ROOT
    title = html.escape(policy.overview_title)
    updated = html.escape(last_updated)
    controls = _controls_html(policy) if policy.show_import_export else ""
    metrics = _metric_cards_html(cards)

    return f"""
    <div class="{r}">
        <section class="overview-section">
            <div class="section-header">
                <div class="title-area">
                    <h2>{title}</h2>
                    <span class="timestamp">Last updated: {updated}</span>
                </div>
                {controls}
            </div>
            <div class="cards-viewport-wrapper">
                <div class="metrics-grid">
                    {metrics}
                </div>
            </div>
        </section>
    </div>
    """


def render_overview_section(
    policy: HubDashboardPolicy,
    last_updated: str,
    cards: list[dict],
) -> None:
    """Render hub overview after Upcoming features (prototype layout + styles)."""
    render_html(build_overview_html(policy, last_updated, cards), width="stretch")
