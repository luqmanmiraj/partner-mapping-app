"""Company profile popup — matches .prototype/popups/decision-maker-popup.html."""

from __future__ import annotations

import html
from typing import Any

from theme.html_utils import render_html

_PREFIX = "nexus-decision-maker-popup"

# Icons as data URIs (DOMPurify strips inline SVG in st.html).
_ICON_ACTIVITY = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 "
    "1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 "
    "1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 "
    "1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'/%3e%3cpath "
    "stroke-linecap='round' stroke-linejoin='round' d='M15 12a3 3 0 11-6 0 3 3 0 016 0z'/%3e%3c/svg%3e"
)
_ICON_STAR = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 "
    "1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 "
    "0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.381-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z'/%3e%3c/svg%3e"
)
_ICON_EMAIL = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 "
    "8.959 0 01-4.5 1.206'/%3e%3c/svg%3e"
)
_ICON_LOCATION = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z'/%3e%3ccircle "
    "stroke-linecap='round' stroke-linejoin='round' cx='12' cy='11' r='2'/%3e%3c/svg%3e"
)
_ICON_GLOBE = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 12H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9'/%3e%3c/svg%3e"
)
_ICON_PHONE = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z'/%3e%3c/svg%3e"
)
_ICON_BUILDING = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5m0 0V9a2 2 0 012-2h2a2 2 0 012 2v12m-6 0h6'/%3e%3c/svg%3e"
)
_ICON_USERS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'/%3e%3c/svg%3e"
)
_ICON_FOLDER = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23d9822b' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-5l-2-2H10z'/%3e%3c/svg%3e"
)
_ICON_FILTER = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%234a4a4a' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4'/%3e%3c/svg%3e"
)
_ICON_MAIL_SMALL = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23777777' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z'/%3e%3c/svg%3e"
)
_ICON_PIN_SMALL = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23777777' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z'/%3e%3ccircle "
    "stroke-linecap='round' stroke-linejoin='round' cx='12' cy='11' r='2'/%3e%3c/svg%3e"
)
_ICON_CHEVRON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23777777' stroke-width='2.5' viewBox='0 0 24 24'%3e%3cpolyline points='6 9 12 15 18 9'/%3e%3c/svg%3e"
)
_ICON_PAGE_PREV = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23111111' stroke-width='2.5' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M15 19l-7-7 7-7'/%3e%3c/svg%3e"
)
_ICON_PAGE_NEXT = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23111111' stroke-width='2.5' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M9 5l7 7-7 7'/%3e%3c/svg%3e"
)


def decision_maker_popup_styles() -> str:
    p = _PREFIX
    icons = {
        "activity": _ICON_ACTIVITY,
        "star": _ICON_STAR,
        "email": _ICON_EMAIL,
        "location": _ICON_LOCATION,
        "globe": _ICON_GLOBE,
        "phone": _ICON_PHONE,
        "building": _ICON_BUILDING,
        "users": _ICON_USERS,
        "folder": _ICON_FOLDER,
        "filter": _ICON_FILTER,
        "mail-sm": _ICON_MAIL_SMALL,
        "pin-sm": _ICON_PIN_SMALL,
        "chevron": _ICON_CHEVRON,
        "page-prev": _ICON_PAGE_PREV,
        "page-next": _ICON_PAGE_NEXT,
    }
    icon_css = "\n".join(
        f".{p}__icon--{name} {{ background-image: url(\"{url}\"); }}"
        for name, url in icons.items()
    )
    return f"""
        .{p} {{
            width: 100%;
            background-color: #ffffff;
            display: flex;
            flex-direction: column;
            gap: 24px;
            box-sizing: border-box;
            color: #111111;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        .{p}__close-bar {{
            display: flex;
            justify-content: flex-end;
            align-items: center;
            font-size: 14px;
            color: #4a4a4a;
            font-weight: 500;
            gap: 4px;
        }}

        .{p}__header-identity {{
            display: flex;
            align-items: center;
            gap: 28px;
            margin-bottom: 8px;
        }}

        .{p}__brand-logo-card {{
            width: 150px;
            height: 150px;
            border: 1px solid #eef0f2;
            border-radius: 4px;
            display: flex;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
            padding: 12px;
            flex-shrink: 0;
        }}

        .{p}__brand-logo-text {{
            font-size: 26px;
            font-weight: 800;
            color: #00965e;
            font-style: italic;
            letter-spacing: -0.5px;
        }}

        .{p}__main-title {{
            font-size: 32px;
            font-weight: 700;
            margin: 0;
            color: #111111;
        }}

        .{p}__meta-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            column-gap: 40px;
            row-gap: 20px;
            margin-bottom: 12px;
        }}

        .{p}__meta-item {{
            display: flex;
            gap: 14px;
            align-items: flex-start;
        }}

        .{p}__meta-icon-box {{
            width: 36px;
            height: 36px;
            background-color: #fdf5e9;
            border-radius: 4px;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-shrink: 0;
        }}

        .{p}__icon {{
            width: 18px;
            height: 18px;
            background: center / contain no-repeat;
            flex-shrink: 0;
        }}

        {icon_css}

        .{p}__meta-texts {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .{p}__meta-label {{
            font-size: 12px;
            font-weight: 700;
            color: #555555;
        }}

        .{p}__meta-value {{
            font-size: 14px;
            color: #222222;
            word-break: break-word;
        }}

        .{p}__tag-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 4px;
        }}

        .{p}__tag-pill {{
            background-color: #fcecdb;
            color: #724010;
            font-size: 13px;
            font-weight: 500;
            padding: 4px 12px;
            border-radius: 4px;
        }}

        .{p}__content-card {{
            background-color: #fafafa;
            border: 1px solid #f0f0f0;
            border-radius: 6px;
            padding: 24px;
            box-sizing: border-box;
        }}

        .{p}__section-title {{
            font-size: 22px;
            font-weight: 700;
            margin: 0 0 16px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .{p}__section-title .{p}__icon {{
            width: 20px;
            height: 20px;
        }}

        .{p}__section-body {{
            font-size: 15px;
            line-height: 1.5;
            color: #555555;
            margin: 0;
        }}

        .{p}__contacts-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}

        .{p}__contact-box {{
            background-color: #ffffff;
            border: 1px solid #eaeaea;
            border-radius: 4px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}

        .{p}__contact-top {{
            background-color: #f1f1f1;
            padding: 16px;
            flex-grow: 1;
        }}

        .{p}__contact-name {{
            font-size: 16px;
            font-weight: 700;
            margin: 0 0 4px 0;
            color: #111111;
        }}

        .{p}__contact-position {{
            font-size: 14px;
            color: #555555;
            margin: 0;
        }}

        .{p}__contact-bottom {{
            padding: 14px 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .{p}__contact-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: #666666;
        }}

        .{p}__contact-meta .{p}__icon {{
            width: 14px;
            height: 14px;
        }}

        .{p}__sub-members-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}

        .{p}__sub-members-bar .{p}__section-title {{
            margin-bottom: 0;
        }}

        .{p}__filter-icon {{
            width: 20px;
            height: 20px;
            background: center / contain no-repeat;
            flex-shrink: 0;
        }}

        .{p}__accordion-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .{p}__accordion-row {{
            background-color: #ffffff;
            border: 1px solid #eaeaea;
            border-radius: 4px;
            padding: 14px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .{p}__accordion-left {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .{p}__accordion-avatar {{
            width: 40px;
            height: 40px;
            background-color: #cccccc;
            border-radius: 4px;
            flex-shrink: 0;
        }}

        .{p}__accordion-meta h4 {{
            font-size: 15px;
            font-weight: 700;
            margin: 0 0 4px 0;
        }}

        .{p}__accordion-sub {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 13px;
            color: #666666;
        }}

        .{p}__accordion-sub .{p}__icon {{
            width: 14px;
            height: 14px;
        }}

        .{p}__pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin-top: 16px;
        }}

        .{p}__page-btn {{
            background: none;
            border: none;
            min-width: 28px;
            height: 28px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            color: #666666;
            cursor: default;
            padding: 0;
        }}

        .{p}__page-btn--active {{
            color: #111111;
            font-weight: 700;
        }}

        .{p}__page-btn .{p}__icon {{
            width: 14px;
            height: 14px;
        }}

        @media (max-width: 768px) {{
            .{p}__meta-grid,
            .{p}__contacts-grid {{
                grid-template-columns: 1fr;
            }}
            .{p}__header-identity {{
                flex-direction: column;
                align-items: flex-start;
                gap: 16px;
            }}
        }}

        /* Streamlit dialog chrome overrides */
        div[data-testid="stDialog"] div[data-testid="stDialogContent"] {{
            padding-top: 0.5rem;
        }}
    """


def inject_decision_maker_popup_styles() -> None:
    render_html(f"<style>{decision_maker_popup_styles()}</style>")


def _meta_item(icon: str, label: str, value_html: str) -> str:
    p = _PREFIX
    return f"""
    <div class="{p}__meta-item">
        <div class="{p}__meta-icon-box">
            <span class="{p}__icon {p}__icon--{icon}" aria-hidden="true"></span>
        </div>
        <div class="{p}__meta-texts">
            <span class="{p}__meta-label">{html.escape(label)}</span>
            {value_html}
        </div>
    </div>
    """


def _tag_pills(products: list[str]) -> str:
    p = _PREFIX
    pills = "".join(
        f'<span class="{p}__tag-pill">{html.escape(item)}</span>' for item in products
    )
    return f'<div class="{p}__tag-container">{pills}</div>'


def _contact_box(contact: dict[str, str]) -> str:
    p = _PREFIX
    return f"""
    <div class="{p}__contact-box">
        <div class="{p}__contact-top">
            <h4 class="{p}__contact-name">{html.escape(contact["name"])}</h4>
            <p class="{p}__contact-position">{html.escape(contact["position"])}</p>
        </div>
        <div class="{p}__contact-bottom">
            <div class="{p}__contact-meta">
                <span class="{p}__icon {p}__icon--pin-sm" aria-hidden="true"></span>
                <span>{html.escape(contact["region"])}</span>
            </div>
            <div class="{p}__contact-meta">
                <span class="{p}__icon {p}__icon--mail-sm" aria-hidden="true"></span>
                <span>{html.escape(contact["email"])}</span>
            </div>
        </div>
    </div>
    """


def _accordion_row(sub_member: dict[str, str]) -> str:
    p = _PREFIX
    return f"""
    <div class="{p}__accordion-row">
        <div class="{p}__accordion-left">
            <div class="{p}__accordion-avatar"></div>
            <div class="{p}__accordion-meta">
                <h4>{html.escape(sub_member["name"])}</h4>
                <div class="{p}__accordion-sub">
                    <span class="{p}__icon {p}__icon--pin-sm" aria-hidden="true"></span>
                    <span>{html.escape(sub_member["location"])}</span>
                </div>
            </div>
        </div>
        <span class="{p}__icon {p}__icon--chevron" aria-hidden="true"></span>
    </div>
    """


def build_decision_maker_popup_html(company: dict[str, Any]) -> str:
    p = _PREFIX
    name = html.escape(str(company["name"]))
    products = company.get("products", [])
    contacts = company.get("contacts", [])
    sub_members = company.get("sub_members", [])

    meta = "".join(
        [
            _meta_item(
                "activity",
                "Activity",
                f'<span class="{p}__meta-value">{html.escape(str(company.get("activity", "")))}</span>',
            ),
            _meta_item("star", "Products", _tag_pills(products)),
            _meta_item(
                "email",
                "General Email",
                f'<span class="{p}__meta-value">{html.escape(str(company.get("email", "")))}</span>',
            ),
            _meta_item(
                "location",
                "Headquarters",
                f'<span class="{p}__meta-value">{html.escape(str(company.get("headquarters", "")))}</span>',
            ),
            _meta_item(
                "globe",
                "Website",
                f'<span class="{p}__meta-value">{html.escape(str(company.get("website", "")))}</span>',
            ),
            _meta_item(
                "phone",
                "Contact Number",
                f'<span class="{p}__meta-value">{html.escape(str(company.get("phone", "")))}</span>',
            ),
        ]
    )

    contacts_html = "".join(_contact_box(c) for c in contacts[:3])
    sub_members_html = "".join(_accordion_row(s) for s in sub_members[:4])

    return f"""
    <div class="{p}">
        <div class="{p}__header-identity">
            <div class="{p}__brand-logo-card">
                <div class="{p}__brand-logo-text">{name}</div>
            </div>
            <h1 class="{p}__main-title">{name}</h1>
        </div>

        <div class="{p}__meta-grid">
            {meta}
        </div>

        <div class="{p}__content-card">
            <h3 class="{p}__section-title">
                <span class="{p}__icon {p}__icon--building" aria-hidden="true"></span>
                About
            </h3>
            <p class="{p}__section-body">{html.escape(str(company.get("about", "")))}</p>
        </div>

        <div class="{p}__content-card">
            <h3 class="{p}__section-title">
                <span class="{p}__icon {p}__icon--star" aria-hidden="true"></span>
                Expertise &amp; Product Ranges
            </h3>
            {_tag_pills(products)}
        </div>

        <div class="{p}__content-card">
            <h3 class="{p}__section-title">
                <span class="{p}__icon {p}__icon--users" aria-hidden="true"></span>
                Key contacts
            </h3>
            <div class="{p}__contacts-grid">
                {contacts_html}
            </div>
        </div>

        <div class="{p}__content-card">
            <div class="{p}__sub-members-bar">
                <h3 class="{p}__section-title">
                    <span class="{p}__icon {p}__icon--folder" aria-hidden="true"></span>
                    Sub-members
                </h3>
                <span class="{p}__filter-icon {p}__icon {p}__icon--filter" aria-hidden="true"></span>
            </div>
            <div class="{p}__accordion-list">
                {sub_members_html}
            </div>
            <div class="{p}__pagination">
                <span class="{p}__page-btn" aria-hidden="true">
                    <span class="{p}__icon {p}__icon--page-prev"></span>
                </span>
                <span class="{p}__page-btn {p}__page-btn--active">1</span>
                <span class="{p}__page-btn">2</span>
                <span class="{p}__page-btn">3</span>
                <span class="{p}__page-btn" aria-hidden="true">
                    <span class="{p}__icon {p}__icon--page-next"></span>
                </span>
            </div>
        </div>
    </div>
    """


def render_decision_maker_popup(company: dict[str, Any]) -> None:
    inject_decision_maker_popup_styles()
    render_html(build_decision_maker_popup_html(company), width="stretch")
