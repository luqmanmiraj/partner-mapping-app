"""Upcoming features info card widget."""

from __future__ import annotations

import html

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.html_utils import render_html


def render_upcoming_features(policy: HubDashboardPolicy) -> None:
    render_html(
        f"""
        <div class="card feature-card">
            <div class="feature-icon">▦</div>
            <div>
                <h3>Upcoming features</h3>
                <p>{html.escape(policy.upcoming_blurb)}</p>
            </div>
        </div>
        """
    )
