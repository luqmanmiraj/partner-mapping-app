"""My Company profile overview — matches .prototype/company/overview.html."""

from __future__ import annotations

import html
from typing import Any

from theme.html_utils import render_st_html_page

_PREFIX = "nexus-company-overview"
_BANNER_IMAGE = (
    "https://images.unsplash.com/photo-1503376780353-7e6692767b70?"
    "auto=format&fit=crop&w=1200&q=80"
)

_ICON_WRENCH = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z'/%3e%3c/svg%3e"
)
_ICON_STAR = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 "
    "1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 "
    "0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.381-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z'/%3e%3c/svg%3e"
)
_ICON_MAIL = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'/%3e%3c/svg%3e"
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
_ICON_PHONE = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23f39c12' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z'/%3e%3c/svg%3e"
)
_ICON_EDIT = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23777777' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M12 20h9M16.5 3.5a2.121 2.121 0 113 3L7 19l-4 1 1-4 12.5-12.5z'/%3e%3c/svg%3e"
)


def company_overview_styles() -> str:
    p = _PREFIX
    icons = {
        "wrench": _ICON_WRENCH,
        "star": _ICON_STAR,
        "mail": _ICON_MAIL,
        "location": _ICON_LOCATION,
        "globe": _ICON_GLOBE,
        "phone": _ICON_PHONE,
        "edit": _ICON_EDIT,
    }
    icon_css = "\n".join(
        f".{p}__icon--{name} {{ background-image: url(\"{url}\"); }}"
        for name, url in icons.items()
    )
    return f"""
        .{p} {{
            width: 100%;
            margin: 0 auto 1.5rem;
            background-color: #ffffff;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #111111;
        }}

        .{p}__banner {{
            position: relative;
            height: 220px;
            background: #0f233c url("{_BANNER_IMAGE}") center/cover no-repeat;
            display: flex;
            justify-content: flex-end;
            padding: 20px 30px;
        }}

        .{p}__banner-overlay {{
            position: absolute;
            inset: 0;
            background: linear-gradient(to right, rgba(15, 35, 60, 0.4), rgba(15, 35, 60, 0.1));
        }}

        .{p}__banner-actions {{
            position: relative;
            z-index: 5;
            display: flex;
            gap: 14px;
            align-items: center;
        }}

        .{p}__edit-banner,
        .{p}__social-link {{
            color: #ffffff;
            text-decoration: none;
            opacity: 0.85;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .{p}__edit-banner {{
            background-color: rgba(255, 255, 255, 0.25);
            width: 28px;
            height: 28px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}

        .{p}__edit-banner-icon {{
            width: 14px;
            height: 14px;
            background: center / contain no-repeat;
            filter: brightness(0) invert(1);
        }}

        .{p}__info {{
            position: relative;
            padding: 30px 40px 40px 240px;
            min-height: 240px;
        }}

        .{p}__logo-frame {{
            position: absolute;
            top: -110px;
            left: 30px;
            width: 180px;
            height: 180px;
            background-color: #ffffff;
            border-radius: 6px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
        }}

        .{p}__logo {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .{p}__logo-circle {{
            width: 34px;
            height: 34px;
            border: 3px solid #111111;
            border-radius: 50%;
            position: relative;
        }}

        .{p}__logo-circle::before {{
            content: '';
            position: absolute;
            width: 3px;
            height: 20px;
            background-color: #111111;
            transform: rotate(15deg);
            top: 5px;
            left: 14px;
        }}

        .{p}__logo-circle::after {{
            content: '';
            position: absolute;
            width: 14px;
            height: 3px;
            background-color: #111111;
            top: 15px;
            left: 8px;
        }}

        .{p}__logo-text {{
            font-size: 2.1rem;
            font-weight: 800;
            color: #e31b23;
            letter-spacing: -0.5px;
        }}

        .{p}__edit-profile {{
            position: absolute;
            top: 30px;
            right: 30px;
            background-color: #f2f2f2;
            width: 32px;
            height: 32px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .{p}__edit-profile-icon {{
            width: 16px;
            height: 16px;
            background: center / contain no-repeat;
        }}

        .{p}__title {{
            font-size: 1.9rem;
            font-weight: 800;
            margin: 0 0 30px 0;
            letter-spacing: -0.5px;
        }}

        .{p}__meta-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            column-gap: 50px;
            row-gap: 24px;
        }}

        .{p}__meta-cell {{
            display: flex;
            align-items: flex-start;
            gap: 14px;
        }}

        .{p}__icon-badge {{
            border: 1.5px solid #f39c12;
            background-color: #fffdf9;
            border-radius: 35%;
            width: 34px;
            height: 34px;
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

        {icon_css}

        .{p}__meta-content {{
            display: flex;
            flex-direction: column;
        }}

        .{p}__meta-label {{
            font-size: 0.85rem;
            color: #666666;
            font-weight: 600;
            margin-bottom: 3px;
        }}

        .{p}__meta-value,
        .{p}__meta-link {{
            font-size: 0.95rem;
            color: #111111;
            text-decoration: none;
        }}

        .{p}__meta-link:hover {{
            text-decoration: underline;
            color: #f39c12;
        }}

        .{p}__tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 2px;
        }}

        .{p}__tag {{
            background-color: #fdeed6;
            color: #4a3319;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 6px;
        }}

        @media (max-width: 850px) {{
            .{p}__info {{
                padding: 100px 20px 30px;
                text-align: center;
            }}
            .{p}__logo-frame {{
                left: 50%;
                transform: translateX(-50%);
                top: -90px;
            }}
            .{p}__meta-grid {{
                grid-template-columns: 1fr;
            }}
            .{p}__meta-cell {{
                flex-direction: column;
                align-items: center;
            }}
            .{p}__tags {{
                justify-content: center;
            }}
        }}
    """


def _meta_cell(icon: str, label: str, value_html: str) -> str:
    p = _PREFIX
    return f"""
    <div class="{p}__meta-cell">
        <div class="{p}__icon-badge">
            <span class="{p}__icon {p}__icon--{icon}" aria-hidden="true"></span>
        </div>
        <div class="{p}__meta-content">
            <span class="{p}__meta-label">{html.escape(label)}</span>
            {value_html}
        </div>
    </div>
    """


def build_company_overview_html(data: dict[str, Any]) -> str:
    p = _PREFIX
    name = html.escape(str(data["company_name"]))
    logo_text = html.escape(str(data.get("logo_text", "BOSCH")))
    products = data.get("products", [])
    tags = "".join(f'<span class="{p}__tag">{html.escape(tag)}</span>' for tag in products)
    social = "".join(
        f'<span class="{p}__social-link">{html.escape(label[0])}</span>'
        for label, _url in data.get("social_links", [])
    )

    meta = "".join(
        [
            _meta_cell("wrench", "Activity", f'<span class="{p}__meta-value">{html.escape(str(data["activity"]))}</span>'),
            _meta_cell("star", "Products", f'<div class="{p}__tags">{tags}</div>'),
            _meta_cell(
                "mail",
                "General Email",
                f'<a class="{p}__meta-link" href="mailto:{html.escape(str(data["email"]))}">'
                f'{html.escape(str(data["email"]))}</a>',
            ),
            _meta_cell("location", "Headquarters", f'<span class="{p}__meta-value">{html.escape(str(data["headquarters"]))}</span>'),
            _meta_cell(
                "globe",
                "Website",
                f'<a class="{p}__meta-link" href="{html.escape(str(data["website_url"]))}" target="_blank" rel="noopener">'
                f'{html.escape(str(data["website_label"]))}</a>',
            ),
            _meta_cell(
                "phone",
                "Contact Number",
                f'<a class="{p}__meta-link" href="tel:{html.escape(str(data["phone"]).replace(" ", ""))}">'
                f'{html.escape(str(data["phone"]))}</a>',
            ),
        ]
    )

    return f"""
    <div class="{p}">
        <div class="{p}__banner">
            <div class="{p}__banner-overlay"></div>
            <div class="{p}__banner-actions">
                <span class="{p}__edit-banner" aria-hidden="true">
                    <span class="{p}__edit-banner-icon {p}__icon--edit"></span>
                </span>
                {social}
            </div>
        </div>
        <div class="{p}__info">
            <div class="{p}__logo-frame">
                <div class="{p}__logo">
                    <div class="{p}__logo-circle"></div>
                    <span class="{p}__logo-text">{logo_text}</span>
                </div>
            </div>
            <span class="{p}__edit-profile" aria-hidden="true">
                <span class="{p}__edit-profile-icon {p}__icon--edit"></span>
            </span>
            <h1 class="{p}__title">{name}</h1>
            <div class="{p}__meta-grid">{meta}</div>
        </div>
    </div>
    """


def inject_company_overview_styles() -> None:
    from theme.html_utils import inject_parent_styles

    inject_parent_styles(company_overview_styles(), style_id="nexus-company-overview")


def render_company_overview(data: dict[str, Any]) -> None:
    render_st_html_page(
        company_overview_styles(),
        build_company_overview_html(data),
        width="stretch",
    )
