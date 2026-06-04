"""Reusable workflow log controls for dashboards (native Streamlit widgets only)."""

from __future__ import annotations

import streamlit as st

from services.workflow_log import list_logs
from theme.html_utils import inject_parent_styles
from theme.tokens import ORANGE, TEXT_MUTED, TEXT_PRIMARY
from widgets.workflow_logs_panel import render_workflow_logs_panel

_STRIP_PREFIX = "nexus-hub-logs-strip"


def _inject_strip_styles(strip_key: str) -> None:
    """Ensure the log strip and its buttons are never collapsed in the main canvas."""
    scope = f'[data-testid="stMain"] .st-key-{strip_key}'
    p = _STRIP_PREFIX
    inject_parent_styles(
        f"""
        {scope} {{
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            position: relative !important;
            z-index: 25 !important;
            width: 100% !important;
            min-height: 72px !important;
            margin: 0 0 1.25rem 0 !important;
            padding: 0.9rem 1rem !important;
            background: #ffffff !important;
            border: 1px solid #e8eaed !important;
            border-left: 4px solid {ORANGE} !important;
            border-radius: 10px !important;
            box-sizing: border-box !important;
            overflow: visible !important;
        }}

        {scope} [data-testid="stElementContainer"],
        {scope} [data-testid="stVerticalBlock"],
        {scope} [data-testid="stHorizontalBlock"],
        {scope} div[data-testid="stButton"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            height: auto !important;
            min-height: 40px !important;
            overflow: visible !important;
        }}

        {scope} .{p}__title {{
            margin: 0 0 0.35rem 0;
            font-size: 1rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
        }}

        {scope} .{p}__meta {{
            margin: 0 0 0.75rem 0;
            font-size: 0.82rem;
            color: {TEXT_MUTED};
        }}

        {scope} div[data-testid="stButton"] > button {{
            min-height: 42px !important;
            font-weight: 600 !important;
        }}

        {scope} div[data-testid="stButton"] > button[kind="primary"] {{
            background: {ORANGE} !important;
            border-color: {ORANGE} !important;
        }}
        """,
        style_id=f"nexus-workflow-strip-{strip_key}",
    )


def render_hub_dashboard_logs_above_hero(
    *,
    partner_key: str | None = None,
    strip_key: str = "hub_workflow_logs_strip",
    view_button_key: str = "hub_logs_view_btn",
    page_button_key: str = "hub_logs_page_btn",
    session_flag: str = "show_workflow_logs_hub",
    title: str = "Workflow activity log",
    link_to_app_page: bool = True,
) -> None:
    """
    Always-visible log controls placed above the welcome hero on Hub Dashboard.

    Uses only native Streamlit widgets (no st.html) so buttons render reliably.
    """
    entries = list_logs(partner_key=partner_key, limit=500)
    is_open = bool(st.session_state.get(session_flag, False))
    count_label = f"{len(entries)} event(s)"
    if partner_key:
        count_label += f" for {partner_key}"

    _inject_strip_styles(strip_key)

    with st.container(key=strip_key):
        st.markdown(
            f'<p class="{_STRIP_PREFIX}__title">Workflow activity</p>'
            f'<p class="{_STRIP_PREFIX}__meta">{count_label} — upload, review, and mapping saves. '
            f"Logs appear here after you upload or review; the button is always available.</p>",
            unsafe_allow_html=True,
        )

        if link_to_app_page:
            btn_left, btn_right = st.columns(2)
        else:
            btn_left = st.columns(1)[0]
            btn_right = None

        with btn_left:
            view_label = "Hide logs" if is_open else "View logs"
            if st.button(
                view_label,
                type="primary",
                key=view_button_key,
                use_container_width=True,
            ):
                st.session_state[session_flag] = not is_open
                st.rerun()
        if btn_right is not None:
            with btn_right:
                if st.button(
                    "Open activity log page",
                    type="secondary",
                    key=page_button_key,
                    use_container_width=True,
                ):
                    st.session_state.navigate_to = "logs"
                    st.rerun()

        if is_open:
            st.markdown(f"#### {title}")
            render_workflow_logs_panel(partner_key=partner_key, limit=100)


def render_workflow_logs_controls(
    *,
    partner_key: str | None = None,
    button_key: str = "view_workflow_logs",
    session_flag: str = "show_workflow_logs",
    title: str = "Upload & review activity",
    strip_key: str | None = None,
    link_to_app_page: bool = True,
) -> None:
    """Financial Dashboard and other pages — same strip as hub when strip_key is set."""
    key = strip_key or f"{button_key}_strip"
    render_hub_dashboard_logs_above_hero(
        partner_key=partner_key,
        strip_key=key,
        view_button_key=button_key,
        page_button_key=f"{button_key}_open_page",
        session_flag=session_flag,
        title=title,
        link_to_app_page=link_to_app_page,
    )
