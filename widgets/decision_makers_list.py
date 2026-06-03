"""Company directory list — matches .prototype/sections/decision-makers.html."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from data.member_directory_fixtures import get_company
from theme.html_utils import render_html
from widgets.decision_maker_popup import render_decision_maker_popup

_PREFIX = "nexus-decision-makers"
_LIST_KEY = "decision_makers_list"

_LOCATION_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23757575' stroke-width='2' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z'/%3e%3ccircle "
    "stroke-linecap='round' stroke-linejoin='round' cx='12' cy='11' r='2'/%3e%3c/svg%3e"
)
_ARROW_ICON = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='currentColor' stroke-width='2.5' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M14 5l7 7m0 0l-7 7m7-7H3'/%3e%3c/svg%3e"
)
_PAGE_PREV = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23111111' stroke-width='2.5' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M15 19l-7-7 7-7'/%3e%3c/svg%3e"
)
_PAGE_NEXT = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' "
    "stroke='%23111111' stroke-width='2.5' viewBox='0 0 24 24'%3e%3cpath stroke-linecap='round' "
    "stroke-linejoin='round' d='M9 5l7 7-7 7'/%3e%3c/svg%3e"
)


def decision_makers_styles() -> str:
    p = _PREFIX
    return f"""
        [data-testid="stMain"] .st-key-{_LIST_KEY} {{
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 16px !important;
        }}

        [data-testid="stMain"] .st-key-{_LIST_KEY} > div {{
            width: 100% !important;
        }}

        .{p}__card {{
            background-color: #ffffff;
            border-radius: 6px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            display: flex;
            flex-direction: column;
            gap: 16px;
            position: relative;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        .{p}__badge-wrap {{
            display: flex;
        }}

        .{p}__badge {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 6px 12px;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .{p}__badge--member {{
            background-color: #d9822b;
            color: #ffffff;
        }}

        .{p}__badge--affiliate {{
            border: 1px solid #d9822b;
            color: #d9822b;
            background-color: transparent;
        }}

        .{p}__card-body {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}

        .{p}__info-group {{
            display: flex;
            align-items: center;
            gap: 20px;
            min-width: 0;
        }}

        .{p}__logo {{
            font-size: 18px;
            font-weight: 800;
            color: #00965e;
            font-style: italic;
            letter-spacing: -0.5px;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .{p}__details h3 {{
            font-size: 20px;
            font-weight: 700;
            color: #111111;
            margin: 0 0 4px 0;
        }}

        .{p}__location {{
            display: flex;
            align-items: center;
            gap: 4px;
            color: #757575;
            font-size: 15px;
        }}

        .{p}__location-icon {{
            width: 16px;
            height: 16px;
            background: center / contain no-repeat url("{_LOCATION_ICON}");
            flex-shrink: 0;
        }}

        .{p}__profile-link {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #111111;
            font-size: 15px;
            font-weight: 700;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .{p}__arrow-icon {{
            width: 16px;
            height: 16px;
            background: center / contain no-repeat url("{_ARROW_ICON}");
        }}

        .{p}__pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin-top: 16px;
            padding: 12px;
            width: 100%;
            box-sizing: border-box;
        }}

        .{p}__page-item {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 32px;
            height: 32px;
            border: none;
            background: none;
            font-size: 15px;
            font-weight: 600;
            color: #4a4a4a;
        }}

        .{p}__page-item--active {{
            color: #111111;
            font-weight: 700;
        }}

        .{p}__page-arrow {{
            width: 18px;
            height: 18px;
            background: center / contain no-repeat;
        }}

        .{p}__page-arrow--prev {{
            background-image: url("{_PAGE_PREV}");
        }}

        .{p}__page-arrow--next {{
            background-image: url("{_PAGE_NEXT}");
        }}

        @media (max-width: 600px) {{
            .{p}__card-body {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .{p}__profile-link {{
                align-self: flex-end;
            }}
        }}

        [data-testid="stMain"] [class*="st-key-dm_card_"] {{
            position: relative !important;
        }}

        [data-testid="stMain"] [class*="st-key-dm_profile_"] {{
            position: absolute !important;
            top: 0 !important;
            right: 0 !important;
            width: 150px !important;
            height: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            z-index: 5 !important;
            pointer-events: none !important;
        }}

        [data-testid="stMain"] [class*="st-key-dm_profile_"] button {{
            width: 100% !important;
            height: 100% !important;
            min-height: 48px !important;
            opacity: 0 !important;
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
            cursor: pointer !important;
            padding: 0 !important;
            margin: 0 !important;
            pointer-events: auto !important;
        }}

        [data-testid="stMain"] [class*="st-key-dm_card_"]:has([class*="st-key-dm_profile_"] button:hover) .{p}__profile-link {{
            color: #d9822b;
        }}
    """


def inject_decision_makers_styles() -> None:
    render_html(f"<style>{decision_makers_styles()}</style>")


def _badge_html(company: dict[str, Any]) -> str:
    p = _PREFIX
    badge = company.get("badge", "member")
    if badge == "affiliate":
        parent = html.escape(str(company.get("parent_company", "Parent Company")))
        return f"""
        <div class="{p}__badge-wrap">
            <span class="{p}__badge {p}__badge--affiliate">
                <span>☆</span> Affiliate {parent}
            </span>
        </div>
        """
    return f"""
    <div class="{p}__badge-wrap">
        <span class="{p}__badge {p}__badge--member">
            <span>★</span> Member
        </span>
    </div>
    """


def _company_card_html(company: dict[str, Any]) -> str:
    p = _PREFIX
    name = html.escape(str(company["name"]))
    location = html.escape(str(company.get("location", "")))
    return f"""
    <div class="{p}__card">
        {_badge_html(company)}
        <div class="{p}__card-body">
            <div class="{p}__info-group">
                <div class="{p}__logo">{name}</div>
                <div class="{p}__details">
                    <h3>{name}</h3>
                    <div class="{p}__location">
                        <span class="{p}__location-icon" aria-hidden="true"></span>
                        <span>{location}</span>
                    </div>
                </div>
            </div>
            <div class="{p}__profile-link" aria-hidden="true">
                <span>See profile</span>
                <span class="{p}__arrow-icon" aria-hidden="true"></span>
            </div>
        </div>
    </div>
    """


def _pagination_html() -> str:
    p = _PREFIX
    return f"""
    <div class="{p}__pagination">
        <span class="{p}__page-item" aria-hidden="true">
            <span class="{p}__page-arrow {p}__page-arrow--prev"></span>
        </span>
        <span class="{p}__page-item {p}__page-item--active">1</span>
        <span class="{p}__page-item">2</span>
        <span class="{p}__page-item">3</span>
        <span class="{p}__page-item" aria-hidden="true">
            <span class="{p}__page-arrow {p}__page-arrow--next"></span>
        </span>
    </div>
    """


@st.dialog("Company profile", width="large", dismissible=True)
def _show_company_profile(company_id: str) -> None:
    company = get_company(company_id)
    if not company:
        st.error("Company profile not found.")
        return
    render_decision_maker_popup(company)


def render_decision_makers_list(companies: list[dict[str, Any]]) -> None:
    inject_decision_makers_styles()

    with st.container(key=_LIST_KEY):
        for company in companies:
            company_id = str(company["id"])
            safe_key = company_id.replace("-", "_")
            with st.container(key=f"dm_card_{safe_key}"):
                render_html(_company_card_html(company), width="stretch")
                with st.container(key=f"dm_profile_{safe_key}"):
                    if st.button(
                        "\u200b",
                        key=f"dm_profile_btn_{safe_key}",
                        help=f"See profile for {company['name']}",
                        type="tertiary",
                    ):
                        _show_company_profile(company_id)

    render_html(_pagination_html(), width="stretch")
