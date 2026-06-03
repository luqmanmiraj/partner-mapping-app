"""Strategic pillars section — matches .prototype/company/pillars.html."""

from __future__ import annotations

import html
from typing import Any

from theme.html_utils import render_html

_PREFIX = "nexus-about-pillars"
_FEATURE_IMAGE = (
    "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?"
    "auto=format&fit=crop&w=600&q=80"
)
_ICON_USERS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'/%3e%3c/svg%3e"
)


def about_pillars_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            width: 100%;
            max-width: 1140px;
            margin: 0 auto 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 40px;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        .{p}__title {{
            font-size: 1.9rem;
            font-weight: 800;
            color: #111111;
            margin: 0 0 25px 0;
            letter-spacing: -0.5px;
        }}

        .{p}__grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
        }}

        .{p}__card {{
            background-color: #ffffff;
            border-radius: 6px;
            padding: 30px 25px 40px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.015);
            box-sizing: border-box;
        }}

        .{p}__card-icon {{
            width: 22px;
            height: 22px;
            background: center / contain no-repeat url("{_ICON_USERS}");
            margin-bottom: 16px;
        }}

        .{p}__card h3 {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #111111;
            margin: 0 0 14px 0;
        }}

        .{p}__card p {{
            font-size: 0.95rem;
            line-height: 1.55;
            color: #555555;
            margin: 0;
        }}

        .{p}__feature {{
            background-color: #ffffff;
            border-radius: 6px;
            padding: 45px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.015);
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 45px;
            align-items: start;
            box-sizing: border-box;
        }}

        .{p}__feature-title {{
            font-size: 2rem;
            font-weight: 800;
            color: #111111;
            margin: 0 0 24px 0;
        }}

        .{p}__feature-desc {{
            font-size: 1.05rem;
            line-height: 1.6;
            color: #555555;
            margin: 0 0 30px 0;
        }}

        .{p}__highlight {{
            color: #f39c12;
            font-weight: 700;
        }}

        .{p}__list {{
            display: flex;
            flex-direction: column;
            gap: 25px;
        }}

        .{p}__list-item {{
            display: flex;
            gap: 16px;
            align-items: flex-start;
        }}

        .{p}__list-icon {{
            width: 20px;
            height: 20px;
            background: center / contain no-repeat url("{_ICON_USERS}");
            margin-top: 4px;
            flex-shrink: 0;
        }}

        .{p}__list-text h4 {{
            font-size: 1.15rem;
            font-weight: 700;
            color: #111111;
            margin: 0 0 6px 0;
        }}

        .{p}__list-text p {{
            font-size: 0.95rem;
            line-height: 1.55;
            color: #555555;
            margin: 0;
        }}

        .{p}__media {{
            width: 100%;
            min-height: 350px;
            background: #07111e url("{_FEATURE_IMAGE}") center/cover no-repeat;
            border-radius: 6px;
        }}

        @media (max-width: 992px) {{
            .{p}__grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .{p}__feature {{
                grid-template-columns: 1fr;
                gap: 35px;
                padding: 30px;
            }}
            .{p}__media {{
                min-height: 300px;
                order: -1;
            }}
        }}

        @media (max-width: 650px) {{
            .{p}__grid {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .{p}__title,
            .{p}__feature-title {{
                font-size: 1.6rem;
            }}
        }}
    """


def inject_about_pillars_styles() -> None:
    render_html(f"<style>{about_pillars_styles()}</style>")


def _pillar_card_html(pillar: dict[str, str]) -> str:
    p = _PREFIX
    return f"""
    <div class="{p}__card">
        <div class="{p}__card-icon" aria-hidden="true"></div>
        <h3>{html.escape(pillar["title"])}</h3>
        <p>{html.escape(pillar["description"])}</p>
    </div>
    """


def build_about_pillars_html(
    pillars: list[dict[str, str]],
    feature: dict[str, Any],
) -> str:
    p = _PREFIX
    cards = "".join(_pillar_card_html(item) for item in pillars)
    list_items = "".join(
        f"""
        <div class="{p}__list-item">
            <div class="{p}__list-icon" aria-hidden="true"></div>
            <div class="{p}__list-text">
                <h4>{html.escape(item["title"])}</h4>
                <p>{html.escape(item["description"])}</p>
            </div>
        </div>
        """
        for item in feature.get("items", [])
    )

    return f"""
    <div class="{p}">
        <section>
            <h2 class="{p}__title">Our Strategic Pillars</h2>
            <div class="{p}__grid">{cards}</div>
        </section>
        <section class="{p}__feature">
            <div class="{p}__feature-content">
                <h2 class="{p}__feature-title">{html.escape(str(feature["title"]))}</h2>
                <p class="{p}__feature-desc">{feature["description"]}</p>
                <div class="{p}__list">{list_items}</div>
            </div>
            <div class="{p}__media" aria-hidden="true"></div>
        </section>
    </div>
    """


def render_about_pillars(
    pillars: list[dict[str, str]],
    feature: dict[str, Any],
) -> None:
    inject_about_pillars_styles()
    render_html(build_about_pillars_html(pillars, feature), width="stretch")
