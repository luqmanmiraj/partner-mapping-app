"""Role-based notification content policy."""

from __future__ import annotations

import streamlit as st

from auth.session import UserSession, get_session
from data.notification_fixtures import NotificationItem, get_notifications


def apply_notification_policy(session: UserSession | None = None) -> list[NotificationItem]:
    """
    Same notification UI for all roles; content filtered/extended by role.
    Base list from session state; role-specific items appended on first load.
    """
    session = session or get_session()
    items = get_notifications()

    if st.session_state.get("_notification_policy_applied"):
        return _filter_for_role(items, session)

    extras: list[NotificationItem] = []
    if session.role_type == "partner" and session.declarant_type == "supplier":
        extras.append(
            NotificationItem(
                id="n-sup-1",
                category="Declaration",
                message="Your April 2026 deposit has been validated.",
                date="Apr, 28",
                notification_type="deposit",
                is_read=False,
            )
        )
    elif session.role_type == "partner" and session.declarant_type == "member":
        extras.append(
            NotificationItem(
                id="n-mem-1",
                category="Declaration",
                message="3 lines from your March deposit require review.",
                date="Apr, 2",
                notification_type="mapping",
                is_read=False,
            )
        )
    elif session.role_type in ("reviewer", "admin"):
        extras.append(
            NotificationItem(
                id="n-rev-1",
                category="Review Queue",
                message="12 mapping proposals are waiting for validation.",
                date="Today",
                notification_type="mapping",
                is_read=False,
            )
        )

    if extras:
        st.session_state.notifications = extras + items
        items = st.session_state.notifications

    st.session_state._notification_policy_applied = True
    return _filter_for_role(items, session)


def _filter_for_role(items: list[NotificationItem], session: UserSession) -> list[NotificationItem]:
    if session.role_type in ("reviewer", "admin"):
        return items
    return items
