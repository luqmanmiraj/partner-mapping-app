"""Internal — Review queue for uploaded files."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from services.memory_store import list_review_entries, snowflake_enabled
from theme.components import render_empty_state, render_page_header, render_section_header
from theme.html_utils import inject_parent_styles, run_parent_script

_MAIN = '[data-testid="stMain"]'
_REVIEW_QUEUE_STYLE_ID = "nexus-review-queue-styles"


def _review_queue_styles() -> str:
    return f"""
        {_MAIN} .st-key-review_queue_shell,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"].st-key-review_queue_shell {{
            max-width: 1000px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }}

        {_MAIN} .st-key-review_queue_toolbar [data-testid="stSelectbox"] > label {{
            font-weight: 600;
        }}

        {_MAIN} .st-key-review_queue_cards [data-testid="stColumn"] {{
            align-self: stretch;
        }}

        {_MAIN} .rev-queue-card {{
            background: #ffffff !important;
            padding: 15px !important;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.03) !important;
            border-radius: 15px !important;
            min-height: 100%;
            transition: box-shadow 0.2s ease;
            border: none !important;
        }}

        {_MAIN} .rev-queue-card:hover {{
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.10) !important;
        }}

        {_MAIN} .rev-queue-card [data-testid="stVerticalBlockBorderWrapper"] {{
            border: none !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
        }}

        {_MAIN} .st-key-review_queue_toolbar button,
        {_MAIN} .rev-queue-card button {{
            background: #000000 !important;
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #000000 !important;
            border-radius: 10px !important;
            transition: background-color 0.2s ease;
        }}

        {_MAIN} .st-key-review_queue_toolbar button:hover,
        {_MAIN} .rev-queue-card button:hover {{
            background: #333333 !important;
            background-color: #333333 !important;
            color: #ffffff !important;
            border-color: #333333 !important;
        }}
    """


def _inject_review_queue_styles() -> None:
    inject_parent_styles(_review_queue_styles(), style_id=_REVIEW_QUEUE_STYLE_ID)


def _assign_rev_queue_card_classes() -> None:
    """Attach ``rev-queue-card`` to each Streamlit card container in the parent DOM."""
    run_parent_script(
        """
        const doc = window.parent.document;
        function apply() {
            doc.querySelectorAll('[class*="st-key-review_queue_card_"]').forEach(function (el) {
                const target =
                    el.getAttribute('data-testid') === 'stVerticalBlockBorderWrapper'
                        ? el
                        : el.querySelector('[data-testid="stVerticalBlockBorderWrapper"]') || el;
                target.classList.add('rev-queue-card');
            });
        }
        apply();
        window.setTimeout(apply, 0);
        window.setTimeout(apply, 150);
        window.setTimeout(apply, 400);
        """
    )


def render(active_page: str = "review_queue") -> None:
    _inject_review_queue_styles()

    with st.container(key="review_queue_shell"):
        render_page_header(subtitle="Uploaded files waiting for manual mapping")

        if snowflake_enabled():
            st.caption("Storage: Snowflake APP schema")
        else:
            st.caption("Storage: in-session fallback (enable **Use Snowflake data** in sidebar)")

        col1, col2, col3 = st.columns([1, 1, 0.5], vertical_alignment="bottom")
        with st.container(key="review_queue_toolbar"):
            with col1:
                partner = st.selectbox("Partner", ["All", "MEYLE", "HELLA", "TMD", "MEMBER_DE_001"])
            with col2:
                status = st.selectbox("Status", ["All", "In review", "Validated"])
            with col3:
                st.write("")
                if st.button("Refresh", use_container_width=True):
                    st.rerun()

        use_sf = st.session_state.get("use_snowflake", False)
        passcode = st.session_state.get("passcode", "")

        with scoped_connection(passcode, force_demo=not use_sf) as conn:
            entries = list_review_entries(
                conn=conn,
                status_filter=status,
                partner_filter=partner,
            )

        render_section_header("Review Queue", subtitle=f"{len(entries)} files ready for review")

        if not entries:
            render_empty_state("No files in queue", "Try changing filters or refreshing the queue.")
            return

        with st.container(key="review_queue_cards"):
            for row_start in range(0, len(entries), 3):
                cols = st.columns(3)
                for i, entry in enumerate(entries[row_start : row_start + 3]):
                    review_id = entry.get("_id", "")
                    upload_id = entry.get("upload_id", "")
                    filename = entry.get("filename", "")
                    partner_key = entry.get("partner_key", "")
                    period = entry.get("period", "")
                    status_value = entry.get("status", "In review")
                    validation_source = entry.get("validation_source", "NONE")
                    source_columns = entry.get("source_columns", []) or []
                    created_at = entry.get("created_at", "")

                    with cols[i]:
                        with st.container(key=f"review_queue_card_{review_id}"):
                            st.markdown(f"**{filename or 'Uploaded File'}**")
                            st.caption(f"Upload ID: {upload_id}")
                            st.write(f"**Partner:** {partner_key}")
                            st.write(f"**Status:** {status_value}")
                            st.write(f"**Period:** {period}")
                            st.write(f"**Columns:** {len(source_columns)}")

                            action_col1, action_col2 = st.columns(2)
                            with action_col1:
                                with st.popover("View Details", use_container_width=True):
                                    st.markdown(f"**Review ID:** `{review_id}`")
                                    st.markdown(f"**Filename:** `{filename}`")
                                    st.markdown(f"**Validation Source:** `{validation_source}`")
                                    st.markdown(f"**Created At:** `{created_at}`")
                                    if source_columns:
                                        st.markdown("**Detected Columns**")
                                        st.write(", ".join(source_columns))
                            with action_col2:
                                if st.button("Review", key=f"review_btn_{review_id}", use_container_width=True):
                                    st.session_state.selected_review_id = review_id
                                    st.session_state.navigate_to = "review_detail"
                                    st.rerun()

        _assign_rev_queue_card_classes()
        _inject_review_queue_styles()
