"""Notifications hover panel — .prototype/sections/notifications.html."""

from __future__ import annotations

import html
import re

from content_policies.notifications import apply_notification_policy
from data.notification_fixtures import NotificationItem
from theme.html_utils import inject_parent_styles, render_html

_PREFIX = "nexus-notifications-dropdown"

_ICON_USERS = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23374151' stroke-width='2' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'/%3e"
    "%3ccircle cx='9' cy='7' r='4'/%3e%3cpath d='M22 21v-2a4 4 0 0 0-3-3.87'/%3e"
    "%3cpath d='M16 3.13a4 4 0 0 1 0 7.75'/%3e%3c/svg%3e"
)
_ICON_CALENDAR = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23374151' stroke-width='2' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3crect x='3' y='4' width='18' height='18' rx='2' ry='2'/%3e"
    "%3cline x1='16' y1='2' x2='16' y2='6'/%3e%3cline x1='8' y1='2' x2='8' y2='6'/%3e"
    "%3cline x1='3' y1='10' x2='21' y2='10'/%3e%3c/svg%3e"
)
_ICON_MAIL = (
    "data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 24 24' fill='none' stroke='%23374151' stroke-width='2' "
    "stroke-linecap='round' stroke-linejoin='round'%3e%3cpath d='M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z'/%3e"
    "%3cpolyline points='22,6 12,13 2,6'/%3e%3c/svg%3e"
)

_ICON_CLASS: dict[str, str] = {
    "new_member": "icon-wrapper--users",
    "your_news": "icon-wrapper--users",
    "event": "icon-wrapper--calendar",
    "whats_new": "icon-wrapper--mail",
    "deposit": "icon-wrapper--mail",
    "mapping": "icon-wrapper--users",
}


def notifications_dropdown_styles() -> str:
    p = _PREFIX
    return f"""
        .{p} .notifications-container {{
            background-color: #ffffff;
            width: 440px;
            max-width: min(440px, calc(100vw - 48px));
            border-radius: 4px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            box-sizing: border-box;
        }}

        .{p} .notifications-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}

        .{p} .notifications-header h2 {{
            font-size: 24px;
            color: #111111;
            margin: 0;
            font-weight: 700;
            line-height: 1.2;
        }}

        .{p} .close-btn {{
            background: none;
            border: none;
            font-size: 28px;
            color: #111111;
            cursor: default;
            line-height: 1;
            padding: 0;
        }}

        .{p} .action-bar {{
            display: flex;
            justify-content: flex-end;
            margin-bottom: 16px;
        }}

        .{p} .mark-all-btn {{
            background: none;
            border: none;
            color: #e68a00;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 0;
        }}

        .{p} .check-icon {{
            font-size: 11px;
        }}

        .{p} .notifications-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .{p} .notification-item {{
            display: flex;
            background-color: #f3f4f6;
            border-radius: 4px;
            padding: 12px;
            gap: 12px;
            position: relative;
            box-sizing: border-box;
        }}

        .{p} .notification-item.unread::before {{
            content: '';
            position: absolute;
            top: 18px;
            left: 54px;
            width: 10px;
            height: 10px;
            background-color: #e68a00;
            border-radius: 50%;
            border: 2px solid #f3f4f6;
            z-index: 2;
        }}

        .{p} .icon-wrapper {{
            background-color: #ffffff;
            width: 48px;
            height: 48px;
            min-width: 48px;
            border-radius: 4px;
            display: flex;
            justify-content: center;
            align-items: center;
            border: 1px solid #e5e7eb;
            background-repeat: no-repeat;
            background-position: center;
            background-size: 20px 20px;
        }}

        .{p} .icon-wrapper--users {{
            background-image: url("{_ICON_USERS}");
        }}

        .{p} .icon-wrapper--calendar {{
            background-image: url("{_ICON_CALENDAR}");
        }}

        .{p} .icon-wrapper--mail {{
            background-image: url("{_ICON_MAIL}");
        }}

        .{p} .notification-content {{
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 0;
        }}

        .{p} .notification-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
            gap: 8px;
        }}

        .{p} .category {{
            font-size: 13px;
            font-weight: 700;
            color: #4b5563;
        }}

        .{p} .date {{
            font-size: 12px;
            color: #6b7280;
            flex-shrink: 0;
        }}

        .{p} .message {{
            font-size: 15px;
            line-height: 1.35;
            color: #1f2937;
            margin: 0;
        }}

        .{p} .message strong {{
            color: #111111;
            font-weight: 600;
        }}

        .{p} .empty-state {{
            font-size: 14px;
            color: #6b7280;
            padding: 8px 0;
        }}
    """


def inject_notifications_dropdown_styles() -> None:
    inject_parent_styles(
        notifications_dropdown_styles(),
        style_id="nexus-notifications-dropdown",
    )


def _message_html(message: str) -> str:
    text = html.escape(message)
    text = re.sub(
        r"\{Title\}",
        "<strong>{Title}</strong>",
        text,
    )
    if "X Company has joined us as a member" in message:
        return "<strong>X Company</strong> has joined us as a member"
    return text.replace("X Company", "<strong>X Company</strong>")


def _notification_item_html(item: NotificationItem) -> str:
    p = _PREFIX
    unread = " unread" if not item.is_read else ""
    icon_class = _ICON_CLASS.get(item.notification_type, "icon-wrapper--users")
    category = html.escape(item.category)
    date = html.escape(item.date)
    message = _message_html(item.message)

    return f"""
            <div class="notification-item{unread}">
                <div class="icon-wrapper {icon_class}" aria-hidden="true"></div>
                <div class="notification-content">
                    <div class="notification-meta">
                        <span class="category">{category}</span>
                        <span class="date">{date}</span>
                    </div>
                    <p class="message">{message}</p>
                </div>
            </div>
    """


def build_notifications_dropdown_html(
    items: list[NotificationItem] | None = None,
) -> str:
    p = _PREFIX
    items = items if items is not None else apply_notification_policy()
    if not items:
        list_html = '<p class="empty-state">No notifications yet.</p>'
    else:
        list_html = "".join(_notification_item_html(item) for item in items)

    return f"""
    <div class="{p}">
        <div class="notifications-container">
            <div class="notifications-header">
                <h2>Notifications</h2>
                <span class="close-btn" aria-hidden="true">&times;</span>
            </div>
            <div class="action-bar">
                <span class="mark-all-btn">
                    <span class="check-icon">✓✓</span> Mark all as read
                </span>
            </div>
            <div class="notifications-list">
                {list_html}
            </div>
        </div>
    </div>
    """
