"""Partner — Declaration upload screen."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from constants import MAX_UPLOAD_BYTES, upload_size_error, upload_size_help
from services.upload_client import upload_declaration
from theme.components import render_page_header, render_section_header
from theme.html_utils import render_html
from theme.tokens import CURRENCIES

_UPLOAD_SCOPE = '[data-testid="stMain"] .st-key-upload_page'


def _inject_upload_styles() -> None:
    """Page-local styles for the centered upload layout."""
    render_html(
        f"""
        <style>
        {_UPLOAD_SCOPE} {{
            max-width: 800px;
            width: 100%;
            margin-left: auto;
            margin-right: auto;
            box-sizing: border-box;
        }}

        {_UPLOAD_SCOPE} .section-header {{
            margin-bottom: 1.25rem;
        }}

        /* Select boxes — light border, no text caret / extra icons */
        {_UPLOAD_SCOPE} [data-testid="stSelectbox"] [data-testid="stSelectboxRootElement"] {{
            border: 1px solid #d1d5db !important;
            border-radius: 6px !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
            min-height: 40px !important;
        }}

        {_UPLOAD_SCOPE} [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            border: none !important;
            background: transparent !important;
            min-height: 38px !important;
            cursor: pointer !important;
        }}

        {_UPLOAD_SCOPE} [data-testid="stSelectbox"] input,
        {_UPLOAD_SCOPE} [data-testid="stSelectbox"] [role="combobox"] {{
            cursor: pointer !important;
            caret-color: transparent !important;
        }}

        {_UPLOAD_SCOPE} [data-testid="stSelectbox"] svg {{
            display: none !important;
        }}

        /* Text area */
        {_UPLOAD_SCOPE} textarea {{
            border-radius: 6px !important;
            border: 1px solid #d1d5db !important;
        }}

        /* File uploader dropzone */
        {_UPLOAD_SCOPE} div[data-testid="stFileUploaderDropzone"] {{
            border-radius: 8px;
            border: 1px dashed #9ca3af;
            background-color: #f9fafb;
        }}

        {_UPLOAD_SCOPE} div[data-testid="stFileUploaderDropzone"]:hover {{
            border-color: #6b7280;
            background-color: #f3f4f6;
        }}

        /* Submit row — button aligned right */
        {_UPLOAD_SCOPE} .st-key-upload_submit_row {{
            display: flex !important;
            justify-content: flex-end !important;
            width: 100% !important;
            margin-top: 0.5rem;
        }}

        {_UPLOAD_SCOPE} .st-key-upload_submit_row [data-testid="stButton"] {{
            width: auto !important;
            flex: 0 0 auto !important;
        }}

        {_UPLOAD_SCOPE} .st-key-upload_submit_row [data-testid="stButton"] > button {{
            width: auto !important;
            min-width: 0 !important;
            padding: 0.55rem 1.5rem !important;
            border-radius: 5px !important;
            background: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #000000 !important;
            font-weight: 600 !important;
        }}

        {_UPLOAD_SCOPE} .st-key-upload_submit_row [data-testid="stButton"] > button:hover {{
            background: #1a1a1a !important;
            color: #ffffff !important;
            border-color: #1a1a1a !important;
        }}

        /* Footer divider + BRD note inside the same column */
        {_UPLOAD_SCOPE} hr {{
            margin: 1.5rem 0 1rem !important;
            border: none !important;
            border-top: 1px solid #e5e7eb !important;
        }}
        </style>
        """
    )


def render(active_page: str = "upload") -> None:
    session = get_session()
    _inject_upload_styles()

    with st.container(key="upload_page"):
        render_page_header(session.display_name, subtitle="Submit a new declaration")

        render_section_header(
            "Declaration Upload",
            subtitle=f"Upload your turnover data — counterparty dimension: {session.counterparty_label}",
        )

        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox(
                "Period",
                ["April 2026", "March 2026", "Q1 2026", "February 2026", "January 2026"],
            )
        with col2:
            currency = st.selectbox(
                "Currency",
                CURRENCIES,
                index=CURRENCIES.index(session.default_currency)
                if session.default_currency in CURRENCIES
                else 0,
            )

        uploaded = st.file_uploader(
            "Drag & drop your file here",
            type=["csv", "xlsx", "xls"],
            help=upload_size_help(),
        )

        comment = st.text_area(
            "Comment (optional)",
            max_chars=500,
            placeholder="Max 500 characters",
        )

        with st.container(key="upload_submit_row"):
            if st.button("Submit declaration", type="primary", key="upload_submit"):
                if uploaded is None:
                    st.error("Please select a file before submitting.")
                elif len(uploaded.getvalue()) > MAX_UPLOAD_BYTES:
                    st.error(upload_size_error())
                else:
                    result = upload_declaration(
                        file_bytes=uploaded.getvalue(),
                        filename=uploaded.name,
                        period=period,
                        currency=currency,
                        comment=comment,
                        partner_key=session.partner_key,
                    )
                    if result.success:
                        st.success(result.message)
                        if result.upload_id:
                            st.info(
                                f"Upload ID: **{result.upload_id}** — Admin can trace all BRD pipeline steps "
                                f"under **Pipeline Monitor**."
                            )
                        st.info(
                            f"Upload ID: **{result.upload_id}** — "
                            "if no memory template exists, this file is now in Reviewer queue."
                        )
                    else:
                        st.error(result.error)

        st.markdown("---")
        st.caption(
            "BRD: Period selector, currency (pre-filled with partner default), "
            "drag & drop upload, optional comment, submit. Processing continues in background."
        )
