"""Notification demo data and session helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import streamlit as st

NotificationType = Literal["new_member", "your_news", "event", "whats_new", "deposit", "mapping"]


@dataclass
class NotificationItem:
    id: str
    category: str
    message: str
    date: str
    notification_type: NotificationType
    is_read: bool = False


ICON_BY_TYPE: dict[str, str] = {
    "new_member": "👥",
    "your_news": "📰",
    "event": "📅",
    "whats_new": "✉️",
    "deposit": "📤",
    "mapping": "📊",
}


def _base_notifications() -> list[NotificationItem]:
    return [
        NotificationItem(
            id="n1",
            category="New Member",
            message="X Company has joined us as a member",
            date="Mar, 17",
            notification_type="new_member",
            is_read=False,
        ),
        NotificationItem(
            id="n2",
            category="Your News",
            message="Your request to publish '{Title}' has been approved and published.",
            date="Mar, 17",
            notification_type="your_news",
            is_read=False,
        ),
        NotificationItem(
            id="n3",
            category="Event",
            message="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            date="Mar, 6",
            notification_type="event",
            is_read=True,
        ),
        NotificationItem(
            id="n4",
            category="What's New",
            message="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            date="Feb, 18",
            notification_type="whats_new",
            is_read=True,
        ),
    ]


def get_notifications() -> list[NotificationItem]:
    if "notifications" not in st.session_state:
        st.session_state.notifications = _base_notifications()
    return st.session_state.notifications


def unread_count() -> int:
    return sum(1 for n in get_notifications() if not n.is_read)


def mark_all_read() -> None:
    for n in get_notifications():
        n.is_read = True


def mark_read(notification_id: str) -> None:
    for n in get_notifications():
        if n.id == notification_id:
            n.is_read = True
            break
