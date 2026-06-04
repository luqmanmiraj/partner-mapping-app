"""Supplier dashboard — workflow log viewer (upload → review → save)."""

from __future__ import annotations

import html

import streamlit as st

from services.workflow_log import list_logs

_PREFIX = "nexus-workflow-logs"
_LOGS_PANEL_MAX_WIDTH = "1000px"
_LOGS_PANEL_CONTAINER_KEY = "workflow_logs_panel"

_LEVEL_META: dict[str, tuple[str, str, str]] = {
    "success": ("✓", "Success", "#059669"),
    "info": ("ℹ", "Info", "#2563eb"),
    "warning": ("⚠", "Warning", "#d97706"),
    "error": ("✕", "Error", "#dc2626"),
    "issue": ("⚑", "Issue", "#7c3aed"),
}


def workflow_logs_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            width: 100%;
            max-width: {_LOGS_PANEL_MAX_WIDTH};
            margin: 0 auto;
            box-sizing: border-box;
        }}

        .{p}__header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }}

        .{p}__title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #111827;
            margin: 0;
        }}

        .{p}__subtitle {{
            font-size: 0.85rem;
            color: #6b7280;
            margin: 0.25rem 0 0 0;
        }}

        .{p}__list {{
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }}

        .{p}__entry {{
            display: grid;
            grid-template-columns: auto 1fr;
            gap: 0.75rem;
            padding: 0.85rem 1rem;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
        }}

        .{p}__badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            font-size: 1rem;
            font-weight: 700;
            flex-shrink: 0;
        }}

        .{p}__body {{
            min-width: 0;
        }}

        .{p}__row1 {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.35rem;
        }}

        .{p}__level {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            color: #ffffff;
        }}

        .{p}__action {{
            font-size: 0.78rem;
            font-weight: 600;
            color: #374151;
            background: #f3f4f6;
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
        }}

        .{p}__time {{
            font-size: 0.75rem;
            color: #9ca3af;
            margin-left: auto;
        }}

        .{p}__message {{
            font-size: 0.9rem;
            color: #111827;
            margin: 0 0 0.25rem 0;
            line-height: 1.4;
        }}

        .{p}__detail {{
            font-size: 0.8rem;
            color: #6b7280;
            margin: 0;
        }}

        .{p}__ids {{
            font-size: 0.75rem;
            color: #9ca3af;
            margin-top: 0.35rem;
        }}

        .{p}__empty {{
            text-align: center;
            padding: 2.5rem 1rem;
            color: #6b7280;
            background: #f9fafb;
            border-radius: 10px;
            border: 1px dashed #d1d5db;
        }}
    """


def _entry_html(entry: dict) -> str:
    p = _PREFIX
    level = str(entry.get("level", "info")).lower()
    icon, label, color = _LEVEL_META.get(level, ("•", level, "#6b7280"))
    message = html.escape(str(entry.get("message", "")))
    detail = html.escape(str(entry.get("detail", "")))
    action = html.escape(str(entry.get("action", "")))
    ts = html.escape(str(entry.get("timestamp", "")))
    upload_id = entry.get("upload_id", "")
    review_id = entry.get("review_id", "")
    ids = ""
    if upload_id or review_id:
        parts = []
        if upload_id:
            parts.append(f"Upload {html.escape(upload_id)}")
        if review_id:
            parts.append(f"Review {html.escape(review_id)}")
        ids = f'<p class="{p}__ids">{" · ".join(parts)}</p>'

    detail_html = f'<p class="{p}__detail">{detail}</p>' if detail else ""
    return f"""
    <article class="{p}__entry">
        <div class="{p}__badge" style="background:{color}22;color:{color};">{icon}</div>
        <div class="{p}__body">
            <div class="{p}__row1">
                <span class="{p}__level" style="background:{color};">{label}</span>
                <span class="{p}__action">{action}</span>
                <span class="{p}__time">{ts}</span>
            </div>
            <p class="{p}__message">{message}</p>
            {detail_html}
            {ids}
        </div>
    </article>
    """


def build_workflow_logs_html(entries: list[dict], *, title: str = "Workflow activity") -> str:
    p = _PREFIX
    if not entries:
        body = (
            f'<div class="{p}__empty">'
            "<strong>No workflow events in this session yet.</strong><br><br>"
            "Upload a declaration under <em>Partner Mapping → Upload</em>, then complete review "
            "to see parse, validation, and mapping steps here."
            "</div>"
        )
    else:
        body = f'<div class="{p}__list">{"".join(_entry_html(e) for e in entries)}</div>'

    return f"""
    <div class="{p}">
        <div class="{p}__header">
            <div>
                <h3 class="{p}__title">{html.escape(title)}</h3>
                <p class="{p}__subtitle">{len(entries)} event(s) — upload, review, and mapping saves</p>
            </div>
        </div>
        {body}
    </div>
    """


def inject_workflow_logs_layout_styles(
    container_key: str = _LOGS_PANEL_CONTAINER_KEY,
) -> None:
    """Center the log panel on the page and cap width at 1000px."""
    from theme.html_utils import inject_parent_styles

    scope = f'[data-testid="stMain"] .st-key-{container_key}'
    inject_parent_styles(
        f"""
        {scope},
        {scope}[data-testid="stVerticalBlockBorderWrapper"] {{
            width: 100% !important;
            max-width: {_LOGS_PANEL_MAX_WIDTH} !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding: 0 !important;
            box-sizing: border-box !important;
        }}

        {scope} [data-testid="stHtml"],
        {scope} [data-testid="stElementContainer"] {{
            width: 100% !important;
            max-width: {_LOGS_PANEL_MAX_WIDTH} !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}

        {scope} [data-testid="stHtml"] iframe {{
            width: 100% !important;
            max-width: 100% !important;
        }}
        """,
        style_id=f"nexus-workflow-logs-layout-{container_key}",
    )


def render_workflow_logs_panel(
    *,
    partner_key: str | None = None,
    limit: int = 100,
    container_key: str = _LOGS_PANEL_CONTAINER_KEY,
) -> None:
    from theme.html_utils import render_st_html_page

    entries = list_logs(partner_key=partner_key, limit=limit)
    inject_workflow_logs_layout_styles(container_key)
    with st.container(key=container_key):
        render_st_html_page(
            workflow_logs_styles(),
            build_workflow_logs_html(entries),
            width="stretch",
        )
