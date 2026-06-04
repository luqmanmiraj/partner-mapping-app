"""Hub portal — workflow logs page (sidebar: Logs)."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session, is_partner, is_reviewer
from services.workflow_log import list_logs
from theme.html_utils import inject_parent_styles, render_html
from theme.tokens import BORDER, CARD_BG
from widgets.workflow_logs_panel import render_workflow_logs_panel

_LOGS_EMPTY_SCOPE = '[data-testid="stMain"] .st-key-logs_empty_state'
_LOGS_EMPTY_STYLE_ID = "nexus-logs-empty-state"


def _inject_logs_empty_styles() -> None:
    """Single empty-state card: message + centered black CTA button inside."""
    scope = _LOGS_EMPTY_SCOPE
    inject_parent_styles(
        f"""
        {scope},
        {scope}[data-testid="stVerticalBlockBorderWrapper"] {{
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            text-align: center !important;
            width: 100% !important;
            max-width: 640px !important;
            margin: 0 auto 1.5rem auto !important;
            padding: 2.5rem 2rem 2rem 2rem !important;
            background: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 12px !important;
            box-sizing: border-box !important;
            box-shadow: none !important;
        }}

        {scope} > div,
        {scope} [data-testid="stHtml"],
        {scope} [data-testid="stElementContainer"] {{
            width: 100% !important;
            max-width: 100% !important;
        }}

        {scope} div[data-testid="stButton"] {{
            display: inline-block !important;
            width: auto !important;
            margin: 1.25rem auto 0 auto !important;
            text-align: center !important;
        }}

        {scope} div[data-testid="stButton"] > button {{
            display: inline-block !important;
            width: auto !important;
            min-width: 0 !important;
            margin: 0 auto !important;
            padding: 0.55rem 1.5rem !important;
            border-radius: 5px !important;
            background: #000000 !important;
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #000000 !important;
            font-weight: 600 !important;
            transition: background-color 0.2s ease, border-color 0.2s ease !important;
        }}

        {scope} div[data-testid="stButton"] > button:hover {{
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
            color: #ffffff !important;
            border-color: #1a1a1a !important;
        }}
        """,
        style_id=_LOGS_EMPTY_STYLE_ID,
    )


def _render_empty_state(*, show_upload_cta: bool) -> None:
    _inject_logs_empty_styles()
    if show_upload_cta:
        body = """
            <p style="margin:0 0 1rem;color:#666666;line-height:1.5;">
                You need to upload a declaration first to view logs.
                After you upload, parsing, review, and mapping steps will appear here.
            </p>
            <p style="margin:0;color:#666666;line-height:1.5;">
                Click <strong>Upload</strong> in the side nav under
                <strong>Partner Mapping</strong> to upload a new declaration.
            </p>
        """
    else:
        body = """
            <p style="margin:0;color:#666666;line-height:1.5;">
                No workflow events have been recorded in this session yet.
            </p>
        """

    with st.container(key="logs_empty_state"):
        render_html(
            f"""
            <div class="nexus-logs-empty-copy">
                <div style="font-size:2.5rem;margin-bottom:0.75rem;">📋</div>
                <h2 style="margin:0 0 0.75rem;font-size:1.25rem;color:#111111;">
                    No logs to display yet
                </h2>
                {body}
            </div>
            """
        )

        if show_upload_cta and st.button(
            "Go to Upload",
            type="primary",
            key="logs_empty_go_upload",
            use_container_width=False,
        ):
            st.session_state.navigate_to = "upload"
            st.rerun()


def render(active_page: str = "logs") -> None:
    session = get_session()
    reviewer_all = is_reviewer() and not session.partner_key
    partner_key = None if reviewer_all else session.partner_key

    entries = list_logs(partner_key=partner_key, limit=200)

    if not entries:
        _render_empty_state(show_upload_cta=is_partner())
        return

    render_workflow_logs_panel(partner_key=partner_key, limit=200)
