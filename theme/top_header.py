"""Top dashboard header — matches .prototype/sections/top-header.html."""

from __future__ import annotations

import html

import streamlit as st

from auth.session import get_session
from content_policies.notifications import apply_notification_policy
from data.notification_fixtures import unread_count
from theme.asset_urls import asset_img_tag
from theme.html_utils import render_html
from theme.paths import icon_path
from widgets.notifications_dropdown import (
    build_notifications_dropdown_html,
    inject_notifications_dropdown_styles,
)
from widgets.user_dropdown import build_user_dropdown_html, inject_user_dropdown_styles

_PREFIX = "nexus-top-header"

_NOTIFICATIONS_ICON = "notifications-icon.png"
_USER_PROFILE_ICON = "user-profile-icon.png"


def top_header_styles() -> str:
    p = _PREFIX
    return f"""
        section.main [data-testid="stMain"] > div {{
            background-color: #f7f9fb;
        }}

        section.main .block-container {{
            padding-top: 0 !important;
        }}

        section.main .st-key-top_header,
        section.main div[data-testid="stVerticalBlockBorderWrapper"].st-key-top_header {{
            position: relative !important;
            padding: 0 !important;
            margin: 0 0 1.5rem 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            width: 100% !important;
            max-width: none !important;
            z-index: 20 !important;
            overflow: visible !important;
            box-sizing: border-box !important;
        }}

        section.main .st-key-top_header > div,
        section.main div.st-key-top_header[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }}

        .{p}__bar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: #ffffff;
            padding: 24px 32px;
            width: 100%;
            box-sizing: border-box;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
            overflow: visible;
        }}

        .{p}__greeting {{
            font-size: 24px;
            font-weight: 700;
            color: #111111;
            letter-spacing: -0.3px;
            margin: 0;
            line-height: 1.2;
        }}

        .{p}__actions {{
            display: flex;
            align-items: center;
            gap: 20px;
            flex-shrink: 0;
        }}

        .{p}__notify-wrap,
        .{p}__profile-wrap {{
            position: relative;
        }}

        /* Invisible bridge so the cursor can reach the panel without losing hover */
        .{p}__notify-wrap::before,
        .{p}__profile-wrap::before {{
            content: "";
            position: absolute;
            left: -8px;
            right: -8px;
            top: 100%;
            height: 14px;
        }}

        .{p}__icon-btn {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 4px;
            border-radius: 50%;
            border: none;
            background: none;
            box-sizing: border-box;
        }}

        .{p}__icon-btn img {{
            display: block;
            width: 22px;
            height: 22px;
            object-fit: contain;
        }}

        .{p}__icon-btn--unread {{
            position: relative;
        }}

        .{p}__icon-btn--unread::after {{
            content: "";
            position: absolute;
            top: 2px;
            right: 2px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #f79400;
        }}

        .{p}__profile-trigger {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 4px 8px;
            border-radius: 6px;
            border: none;
            background: none;
            box-sizing: border-box;
        }}

        .{p}__profile-trigger img.{p}__user-icon {{
            display: block;
            width: 24px;
            height: 24px;
            object-fit: contain;
        }}

        .{p}__profile-trigger .{p}__chevron-icon {{
            display: inline-block;
            flex-shrink: 0;
            width: 14px;
            height: 14px;
            position: relative;
        }}

        .{p}__profile-trigger .{p}__chevron-icon::before {{
            content: "";
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -35%);
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #666666;
        }}

        /* Hover panels — padding-top bridges the gap; high z-index above Streamlit controls */
        .{p}__notify-panel,
        .{p}__profile-panel {{
            display: none;
            position: absolute;
            top: 100%;
            right: 0;
            padding-top: 10px;
            z-index: 100;
            pointer-events: auto;
            box-sizing: border-box;
        }}

        .{p}__notify-wrap:hover .{p}__notify-panel,
        .{p}__profile-wrap:hover .{p}__profile-panel,
        .{p}__notify-panel:hover,
        .{p}__profile-panel:hover,
        section.main .st-key-top_header:has(.{p}__notify-wrap:hover) .{p}__notify-panel,
        section.main .st-key-top_header:has(.{p}__profile-wrap:hover) .{p}__profile-panel,
        section.main .st-key-top_header:has(.{p}__notify-panel:hover) .{p}__notify-panel,
        section.main .st-key-top_header:has(.{p}__profile-panel:hover) .{p}__profile-panel,
        section.main .st-key-top_header:has(.st-key-top_header_notify button:hover) .{p}__notify-panel,
        section.main .st-key-top_header:has(.st-key-top_header_profile button:hover) .{p}__profile-panel {{
            display: block;
        }}

        section.main .st-key-top_header_controls,
        section.main .st-key-top_header_controls [data-testid="stVerticalBlockBorderWrapper"] {{
            position: absolute !important;
            top: 24px !important;
            right: 32px !important;
            width: auto !important;
            height: auto !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            z-index: 50 !important;
            pointer-events: none !important;
        }}

        section.main .st-key-top_header_controls [data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            align-items: flex-start !important;
            gap: 20px !important;
            width: auto !important;
        }}

        section.main .st-key-top_header_controls [data-testid="column"] {{
            width: auto !important;
            flex: 0 0 auto !important;
            min-width: 0 !important;
            padding: 0 !important;
            background: transparent !important;
        }}

        section.main .st-key-top_header_controls .st-key-top_header_notify,
        section.main .st-key-top_header_controls .st-key-top_header_profile {{
            position: relative !important;
            width: 30px !important;
            height: 30px !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            pointer-events: auto !important;
        }}

        section.main .st-key-top_header_controls .st-key-top_header_profile {{
            width: 52px !important;
            height: 32px !important;
        }}

        section.main .st-key-top_header_controls div[data-testid="stButton"] {{
            margin: 0 !important;
            padding: 0 !important;
        }}

        section.main .st-key-top_header_controls .st-key-top_header_notify button,
        section.main .st-key-top_header_controls .st-key-top_header_profile button {{
            width: 100% !important;
            height: 100% !important;
            min-height: 30px !important;
            padding: 0 !important;
            margin: 0 !important;
            opacity: 0 !important;
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
            cursor: pointer !important;
        }}

        section.main .st-key-top_header:has(.st-key-top_header_notify button:hover) .{p}__icon-btn,
        section.main .st-key-top_header:has(.{p}__notify-wrap:hover) .{p}__icon-btn {{
            background-color: #f5f5f5;
        }}

        section.main .st-key-top_header:has(.st-key-top_header_profile button:hover) .{p}__profile-trigger,
        section.main .st-key-top_header:has(.{p}__profile-wrap:hover) .{p}__profile-trigger {{
            background-color: #f5f5f5;
        }}
    """


def inject_top_header_styles() -> None:
    inject_notifications_dropdown_styles()
    inject_user_dropdown_styles()
    render_html(f"<style>{top_header_styles()}</style>")


def _greeting_name(display_name: str) -> str:
    name = (display_name or "User").strip()
    if not name:
        return "User"
    return name.split()[0]


def _bar_html(
    display_name: str,
    *,
    unread: bool,
    notifications_html: str,
    profile_html: str,
) -> str:
    p = _PREFIX
    greeting = html.escape(_greeting_name(display_name))
    bell_class = f"{p}__icon-btn"
    if unread:
        bell_class += f" {p}__icon-btn--unread"

    bell_img = asset_img_tag(
        icon_path(_NOTIFICATIONS_ICON),
        width=22,
        height=22,
        image_id="nexus-top-header-notifications",
    )
    user_img = asset_img_tag(
        icon_path(_USER_PROFILE_ICON),
        css_class=f"{p}__user-icon",
        width=24,
        height=24,
        image_id="nexus-top-header-profile",
    )

    return f"""
    <header class="{p}__bar">
        <h1 class="{p}__greeting">Welcome {greeting},</h1>
        <div class="{p}__actions">
            <div class="{p}__notify-wrap">
                <div class="{bell_class}" aria-label="Notifications">
                    {bell_img}
                </div>
                <div class="{p}__notify-panel">
                    {notifications_html}
                </div>
            </div>
            <div class="{p}__profile-wrap">
                <div class="{p}__profile-trigger" aria-label="User menu">
                    {user_img}
                    <span class="{p}__chevron-icon" aria-hidden="true"></span>
                </div>
                <div class="{p}__profile-panel">
                    {profile_html}
                </div>
            </div>
        </div>
    </header>
    """


def render_top_header(display_name: str) -> None:
    """Render global dashboard header with hover notifications and profile menus."""
    session = get_session()
    unread = unread_count() > 0
    notifications_html = build_notifications_dropdown_html(apply_notification_policy())
    profile_html = build_user_dropdown_html(session)

    with st.container(key="top_header"):
        render_html(
            _bar_html(
                display_name,
                unread=unread,
                notifications_html=notifications_html,
                profile_html=profile_html,
            ),
            width="stretch",
        )

        with st.container(key="top_header_controls"):
            bell_col, profile_col = st.columns(2, gap="small")
            with bell_col:
                with st.container(key="top_header_notify"):
                    st.button(
                        "\u200b",
                        key="top_header_notify_btn",
                        help="Notifications",
                        type="tertiary",
                    )
            with profile_col:
                with st.container(key="top_header_profile"):
                    st.button(
                        "\u200b",
                        key="top_header_profile_btn",
                        help="User menu",
                        type="tertiary",
                    )
