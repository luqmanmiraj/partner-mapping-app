"""Partner — Corrective deposit screen."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from constants import MAX_UPLOAD_BYTES, upload_size_error, upload_size_help
from data.partner_declarations import check_period_closed
from services.upload_client import upload_declaration
from theme.components import render_page_header, render_section_header, render_warning_banner
from theme.html_utils import render_html
from theme.tokens import CURRENCIES

_CORRECTIVE_SCOPE = '[data-testid="stMain"] .st-key-corrective_page'


def _inject_corrective_styles() -> None:
    """Page-local styles for the centered corrective deposit layout."""
    render_html(
        f"""
        <style>
        {_CORRECTIVE_SCOPE} {{
            max-width: 800px;
            width: 100%;
            margin-left: auto;
            margin-right: auto;
            box-sizing: border-box;
        }}

        {_CORRECTIVE_SCOPE} .section-header {{
            margin-bottom: 1.25rem;
        }}

        {_CORRECTIVE_SCOPE} [data-testid="stSelectbox"] [data-testid="stSelectboxRootElement"] {{
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
            min-height: 40px !important;
        }}

        {_CORRECTIVE_SCOPE} [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            border: none !important;
            background: transparent !important;
            min-height: 38px !important;
            cursor: pointer !important;
        }}

        {_CORRECTIVE_SCOPE} [data-testid="stSelectbox"] input,
        {_CORRECTIVE_SCOPE} [data-testid="stSelectbox"] [role="combobox"] {{
            cursor: pointer !important;
            caret-color: transparent !important;
        }}

        {_CORRECTIVE_SCOPE} [data-testid="stSelectbox"] svg {{
            display: none !important;
        }}

        {_CORRECTIVE_SCOPE} [data-testid="stTextInput"] input {{
            border-radius: 6px !important;
            border: 1px solid #d1d5db !important;
        }}

        {_CORRECTIVE_SCOPE} textarea {{
            border-radius: 6px !important;
            border: 1px solid #d1d5db !important;
        }}

        {_CORRECTIVE_SCOPE} div[data-testid="stFileUploaderDropzone"] {{
            border-radius: 8px;
            border: 1px dashed #9ca3af;
            background-color: #f9fafb;
        }}

        {_CORRECTIVE_SCOPE} div[data-testid="stFileUploaderDropzone"]:hover {{
            border-color: #6b7280;
            background-color: #f3f4f6;
        }}

        {_CORRECTIVE_SCOPE} .st-key-corrective_submit_row {{
            display: flex !important;
            justify-content: flex-end !important;
            width: 100% !important;
            margin-top: 0.5rem;
        }}

        {_CORRECTIVE_SCOPE} .st-key-corrective_submit_row [data-testid="stButton"] {{
            width: auto !important;
            flex: 0 0 auto !important;
            display: inline-block !important;
        }}

        {_CORRECTIVE_SCOPE} .st-key-corrective_submit_row [data-testid="stButton"] > button {{
            display: inline-block !important;
            width: auto !important;
            min-width: 0 !important;
            padding: 0.55rem 1.5rem !important;
            border-radius: 10px !important;
            background: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #000000 !important;
            font-weight: 600 !important;
        }}

        {_CORRECTIVE_SCOPE} .st-key-corrective_submit_row [data-testid="stButton"] > button:hover {{
            background: #1a1a1a !important;
            color: #ffffff !important;
            border-color: #1a1a1a !important;
        }}
        </style>
        """
    )


def render(active_page: str = "corrective") -> None:
    session = get_session()
    _inject_corrective_styles()

    with st.container(key="corrective_page"):
        render_page_header(
            session.display_name,
            subtitle="Submit a correction for a previous period",
        )

        render_section_header(
            "Corrective Deposit",
            subtitle="Previous deposit will be marked Superseded — both preserved in history",
        )

        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox(
                "Period to correct",
                ["April 2026", "March 2026", "Q1 2026", "Q4 2025", "December 2025"],
            )
        with col2:
            original_id = st.text_input(
                "Original deposit ID (optional)",
                placeholder="DEP-2026-0042",
            )

        if check_period_closed(session.partner_key, period):
            render_warning_banner(
                f"Period **{period}** is closed. Your correction will not modify the accounting snapshot "
                "— it will generate an alert for the admin to evaluate."
            )

        currency = st.selectbox(
            "Currency",
            CURRENCIES,
            index=CURRENCIES.index(session.default_currency)
            if session.default_currency in CURRENCIES
            else 0,
        )
        uploaded = st.file_uploader(
            "Corrected file",
            type=["csv", "xlsx", "xls"],
            help=upload_size_help(),
        )
        comment = st.text_area("Reason for correction", max_chars=500)

        with st.container(key="corrective_submit_row"):
            if st.button("Submit corrective deposit", type="primary", key="corrective_submit"):
                if uploaded is None:
                    st.error("Please attach the corrected file.")
                elif len(uploaded.getvalue()) > MAX_UPLOAD_BYTES:
                    st.error(upload_size_error())
                else:
                    result = upload_declaration(
                        file_bytes=uploaded.getvalue(),
                        filename=uploaded.name,
                        period=period,
                        currency=currency,
                        comment=f"[CORRECTIVE {original_id}] {comment}",
                        partner_key=session.partner_key,
                        is_corrective=True,
                        supersedes_upload_id=original_id or "",
                    )
                    if result.success:
                        st.success(
                            f"Corrective deposit submitted ({result.upload_id}). "
                            "Previous deposit will be marked Superseded when processing completes."
                        )
                    else:
                        st.error(result.error)
