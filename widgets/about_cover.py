"""About page cover header — matches .prototype/company/cover.html."""

from __future__ import annotations

import html
from typing import Any

from theme.asset_urls import asset_img_tag
from theme.html_utils import render_html
from theme.paths import image_path

_PREFIX = "nexus-about-cover"
_LOGO_FILE = "side-nav-logo.jpg"
_BANNER_IMAGE = (
    "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?"
    "auto=format&fit=crop&w=1100&q=80"
)

_ICON_LOCATION = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z'/%3e%3ccircle "
    "stroke-linecap='round' stroke-linejoin='round' cx='12' cy='11' r='2'/%3e%3c/svg%3e"
)
_ICON_GLOBE = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 12H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9'/%3e%3c/svg%3e"
)


def about_cover_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} {{
            width: 100%;
            max-width: 1100px;
            margin: 0 auto 1.5rem;
            background-color: #ffffff;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        .{p}__banner {{
            position: relative;
            height: 180px;
            background: #060b14 url("{_BANNER_IMAGE}") center/cover no-repeat;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 0 20px;
        }}

        .{p}__banner-overlay {{
            position: absolute;
            inset: 0;
            background: linear-gradient(
                135deg,
                rgba(6, 11, 20, 0.85) 0%,
                rgba(26, 16, 5, 0.8) 100%
            );
        }}

        .{p}__banner-content {{
            position: relative;
            z-index: 2;
        }}

        .{p}__banner-content h1 {{
            color: #ffffff;
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: 1px;
            line-height: 1.25;
            margin: 0;
        }}

        .{p}__highlight {{
            color: #f39c12;
        }}

        .{p}__social {{
            position: absolute;
            top: 15px;
            right: 20px;
            z-index: 3;
            display: flex;
            gap: 12px;
        }}

        .{p}__social-link {{
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 600;
            opacity: 0.85;
            text-decoration: none;
            transition: opacity 0.2s ease;
        }}

        .{p}__social-link:hover {{
            opacity: 1;
        }}

        .{p}__info {{
            position: relative;
            padding: 25px 30px 30px 220px;
            min-height: 140px;
        }}

        .{p}__logo-box {{
            position: absolute;
            top: -90px;
            left: 30px;
            width: 160px;
            height: 160px;
            background-color: #ffffff;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            padding: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
            box-sizing: border-box;
        }}

        .{p}__logo-box img {{
            display: block;
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}

        .{p}__company-name {{
            font-size: 1.65rem;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0 0 20px 0;
        }}

        .{p}__meta {{
            display: grid;
            grid-template-columns: minmax(250px, auto) minmax(250px, auto);
            gap: 30px;
        }}

        .{p}__meta-item {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}

        .{p}__icon-wrap {{
            border: 1.5px solid #f39c12;
            border-radius: 35%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        .{p}__icon {{
            width: 16px;
            height: 16px;
            background: center / contain no-repeat;
        }}

        .{p}__icon--location {{
            background-image: url("{_ICON_LOCATION}");
        }}

        .{p}__icon--globe {{
            background-image: url("{_ICON_GLOBE}");
        }}

        .{p}__meta-text {{
            display: flex;
            flex-direction: column;
        }}

        .{p}__meta-label {{
            font-size: 0.85rem;
            color: #666666;
            font-weight: 600;
            margin-bottom: 2px;
        }}

        .{p}__meta-value,
        .{p}__meta-link {{
            font-size: 0.9rem;
            color: #222222;
            text-decoration: none;
        }}

        .{p}__meta-link:hover {{
            text-decoration: underline;
            color: #f39c12;
        }}

        @media (max-width: 768px) {{
            .{p}__info {{
                padding: 90px 20px 20px;
                text-align: center;
            }}
            .{p}__logo-box {{
                left: 50%;
                transform: translateX(-50%);
                top: -80px;
            }}
            .{p}__meta {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            .{p}__meta-item {{
                flex-direction: column;
                align-items: center;
            }}
            .{p}__banner-content h1 {{
                font-size: 1.4rem;
            }}
        }}
    """


def inject_about_cover_styles() -> None:
    render_html(f"<style>{about_cover_styles()}</style>")


def build_about_cover_html(profile: dict[str, Any]) -> str:
    p = _PREFIX
    headline = html.escape(str(profile["banner_headline"]))
    highlight = html.escape(str(profile["banner_highlight"]))
    name = html.escape(str(profile["name"]))
    hq = html.escape(str(profile["headquarters"]))
    website_label = html.escape(str(profile["website_label"]))
    website_url = html.escape(str(profile["website_url"]))

    logo = asset_img_tag(
        image_path(_LOGO_FILE),
        css_class=f"{p}__logo-img",
        image_id="nexus-about-cover-logo",
    )
    if not logo:
        logo = f'<span class="{p}__logo-fallback">NEXUS</span>'

    social_links = "".join(
        f'<a class="{p}__social-link" href="{html.escape(url)}" aria-label="{html.escape(label)}">'
        f"{html.escape(label[0])}</a>"
        for label, url in profile.get("social_links", [])
    )

    return f"""
    <header class="{p}">
        <div class="{p}__banner">
            <div class="{p}__banner-overlay"></div>
            <div class="{p}__banner-content">
                <h1>{headline}<br><span class="{p}__highlight">{highlight}</span></h1>
            </div>
            <div class="{p}__social">{social_links}</div>
        </div>
        <div class="{p}__info">
            <div class="{p}__logo-box">{logo}</div>
            <h2 class="{p}__company-name">{name}</h2>
            <div class="{p}__meta">
                <div class="{p}__meta-item">
                    <div class="{p}__icon-wrap">
                        <span class="{p}__icon {p}__icon--location" aria-hidden="true"></span>
                    </div>
                    <div class="{p}__meta-text">
                        <span class="{p}__meta-label">Headquarters</span>
                        <span class="{p}__meta-value">{hq}</span>
                    </div>
                </div>
                <div class="{p}__meta-item">
                    <div class="{p}__icon-wrap">
                        <span class="{p}__icon {p}__icon--globe" aria-hidden="true"></span>
                    </div>
                    <div class="{p}__meta-text">
                        <span class="{p}__meta-label">Website</span>
                        <a class="{p}__meta-link" href="{website_url}" target="_blank" rel="noopener">
                            {website_label}
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </header>
    """


def render_about_cover(profile: dict[str, Any]) -> None:
    inject_about_cover_styles()
    render_html(build_about_cover_html(profile), width="stretch")
