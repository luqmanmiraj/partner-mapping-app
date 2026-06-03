"""Upcoming features info card — matches .prototype/sections/upcoming-features.html."""

from __future__ import annotations

import html

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.asset_urls import asset_img_tag
from theme.html_utils import render_st_html_page
from theme.paths import icon_path

_PREFIX = "nexus-upcoming-features"
_UPCOMING_ICON = "upcoming-features-icon.png"


def upcoming_features_styles() -> str:
    p = _PREFIX
    return f"""
        .{p}__banner {{
            width: 100%;
            background: radial-gradient(circle at 10% 20%, #fff7f0 0%, #ffffff 80%);
            border-left: 4px solid #111111;
            border-radius: 4px 12px 12px 4px;
            padding: 24px 32px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
            box-sizing: border-box;
            margin-bottom: 1rem;
        }}

        .{p}__header {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: flex-start;
        }}

        .{p}__icon {{
            display: block;
            width: 36px;
            height: 36px;
            object-fit: contain;
            flex-shrink: 0;
        }}

        .{p}__banner h2 {{
            font-size: 20px;
            font-weight: 700;
            color: #111111;
            letter-spacing: -0.3px;
            margin: 0;
        }}

        .{p}__banner p {{
            font-size: 14.5px;
            line-height: 1.6;
            color: #444444;
            margin: 0;
            max-width: 1050px;
        }}
    """


def render_upcoming_features(policy: HubDashboardPolicy) -> None:
    p = _PREFIX
    icon = asset_img_tag(
        icon_path(_UPCOMING_ICON),
        css_class=f"{p}__icon",
        width=36,
        height=36,
        image_id="nexus-upcoming-features-icon",
    )

    render_st_html_page(
        upcoming_features_styles(),
        f"""
        <section class="{p}__banner">
            <div class="{p}__header">
                {icon}
                <h2>Upcoming features</h2>
            </div>
            <p>{html.escape(policy.upcoming_blurb)}</p>
        </section>
        """,
    )
