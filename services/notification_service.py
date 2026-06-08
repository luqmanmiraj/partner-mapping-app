"""Notifications — Snowflake APP.NOTIFICATION with session fallback."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.notification_fixtures import NotificationItem, get_notifications as get_session_notifications
from services import snowflake_store


def sync_notifications_from_db(partner_key: str) -> None:
    """Merge Snowflake notifications into session list."""
    if not st.session_state.get("use_snowflake", False):
        return
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=False) as conn:
        if conn is None:
            return
        rows = snowflake_store.list_notifications(conn, partner_key)
        if not rows:
            return
        existing = get_session_notifications()
        existing_ids = {n.id for n in existing}
        for r in rows:
            if r["id"] not in existing_ids:
                existing.insert(
                    0,
                    NotificationItem(
                        id=r["id"],
                        category=r["category"],
                        message=r["message"],
                        date=r.get("date", "Today"),
                        notification_type=r.get("notification_type", "deposit"),
                        is_read=r.get("is_read", False),
                    ),
                )
