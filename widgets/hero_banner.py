"""Hero welcome banner — matches .prototype/sections/centeralized-hub.html."""

from __future__ import annotations

import html

from content_policies.hub_dashboard import HubDashboardPolicy
from theme.asset_urls import asset_img_tag
from theme.html_utils import render_st_html_page
from theme.paths import icon_path, image_path

_PREFIX = "nexus-hub-hero"
_HUB_SHOWCASE_IMAGE = "centeral-hub.png"
_LIST_ARROW_ICON = "list-arrow-icon.png"


def hero_banner_styles() -> str:
    p = _PREFIX
    return f"""
        .{p}__banner {{
            width: 100%;
            background: linear-gradient(105deg, #fff5eb 0%, #fbf4ee 50%, #f6e6d9 100%);
            border-radius: 16px;
            padding: 48px 64px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(242, 169, 108, 0.08);
            gap: 40px;
            box-sizing: border-box;
            margin-bottom: 1rem;
        }}

        .{p}__left {{
            flex: 1;
            min-width: 320px;
        }}

        .{p}__left h1 {{
            font-size: 36px;
            font-weight: 600;
            color: #111111;
            margin: 0 0 28px 0;
            letter-spacing: -0.5px;
            line-height: 1.15;
        }}

        .{p}__features-list {{
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .{p}__features-list li {{
            font-size: 18px;
            font-weight: 700;
            color: #111111;
            display: flex;
            align-items: center;
            gap: 14px;
            margin: 0;
        }}

        .{p}__arrow {{
            display: block;
            width: 18px;
            height: 18px;
            flex-shrink: 0;
            object-fit: contain;
        }}

        .{p}__right {{
            display: flex;
            align-items: flex-end;
            justify-content: flex-end;
            flex-shrink: 0;
        }}

        .{p}__showcase {{
            display: block;
            max-width: 100%;
            height: auto;
            max-height: 220px;
            object-fit: contain;
        }}

        @media (max-width: 960px) {{
            .{p}__banner {{
                flex-direction: column;
                align-items: flex-start;
                padding: 40px;
            }}
            .{p}__right {{
                width: 100%;
                justify-content: center;
                margin-top: 20px;
            }}
        }}

        @media (max-width: 480px) {{
            .{p}__left h1 {{ font-size: 28px; }}
            .{p}__features-list li {{ font-size: 15px; }}
            .{p}__right {{ display: none; }}
        }}
    """


def render_hero_banner(policy: HubDashboardPolicy) -> None:
    p = _PREFIX
    arrow = asset_img_tag(
        icon_path(_LIST_ARROW_ICON),
        css_class=f"{p}__arrow",
        width=18,
        height=18,
        image_id="nexus-hub-hero-list-arrow",
    )
    showcase = asset_img_tag(
        image_path(_HUB_SHOWCASE_IMAGE),
        css_class=f"{p}__showcase",
        image_id="nexus-hub-hero-showcase",
    )

    items_html = ""
    for bullet in policy.hero_bullets:
        items_html += (
            f"<li>{arrow}<span>{html.escape(bullet)}</span></li>"
        )

    render_st_html_page(
        hero_banner_styles(),
        f"""
        <section class="{p}__banner">
            <div class="{p}__left">
                <h1>{html.escape(policy.hero_headline)}</h1>
                <ul class="{p}__features-list">{items_html}</ul>
            </div>
            <div class="{p}__right">
                {showcase}
            </div>
        </section>
        """,
    )
