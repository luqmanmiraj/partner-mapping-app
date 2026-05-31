"""Section header with optional filter toolbar."""

from __future__ import annotations

import html

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.html_utils import render_html


def render_section_toolbar(
    title: str,
    last_updated: str,
    *,
    policy: HubDashboardPolicy | None = None,
    show_controls: bool = False,
) -> None:
    controls = ""
    if show_controls and (policy is None or policy.show_import_export):
        filters = policy.filter_labels if policy else ("Date", "Filter")
        f1, f2 = filters[0], filters[1] if len(filters) > 1 else "Filter"
        controls = f"""
            <div class="toolbar">
                <span class="select-pill">{html.escape(f1)} ▾</span>
                <span class="select-pill">{html.escape(f2)} ▾</span>
                <span class="btn-outline">⬆ Import</span>
                <span class="btn-outline">⬇ Export</span>
            </div>
        """
    render_html(
        f"""
        <div class="section-header">
            <div>
                <h2>{html.escape(title)}</h2>
                <div class="subtitle">Last updated: {html.escape(last_updated)}</div>
            </div>
            {controls}
        </div>
        """
    )
