"""Notifications panel widget — shared modal for all roles."""

from __future__ import annotations

import streamlit as st

from content_policies.notifications import apply_notification_policy
from data.notification_fixtures import ICON_BY_TYPE, mark_all_read, unread_count


def _render_notification_card(item) -> None:
    icon = ICON_BY_TYPE.get(item.notification_type, "🔔")
    unread_marker = " 🔴" if not item.is_read else ""

    with st.container(border=True):
        icon_col, body_col = st.columns([1, 9], gap="small")
        with icon_col:
            st.markdown(f"### {icon}{unread_marker}")
        with body_col:
            header_col, date_col = st.columns([3, 1])
            with header_col:
                st.markdown(f"**{item.category}**")
            with date_col:
                st.caption(item.date)
            st.write(item.message)


@st.dialog("Notifications", width="large")
def notifications_dialog() -> None:
    items = apply_notification_policy()

    _, action_col = st.columns([3, 1])
    with action_col:
        if st.button("Mark all as read", key="notif_mark_all", use_container_width=True):
            mark_all_read()
            st.rerun()

    if not items:
        st.info("No notifications yet.")
        return

    for item in items:
        _render_notification_card(item)


def open_notifications_dialog() -> None:
    notifications_dialog()


def render_notification_bell(*, key: str = "header_notifications") -> None:
    """Bell button with unread badge — place in page header row."""
    count = unread_count()
    badge = f" ({count})" if count else ""
    if st.button(f"🔔{badge}", key=key, help="Notifications"):
        open_notifications_dialog()
