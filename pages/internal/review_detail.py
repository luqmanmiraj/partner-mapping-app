"""Internal — Review detail and manual column mapping."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from auth.snowflake_session import scoped_connection
from auth.session import get_session
from services.memory_store import get_review_entry, save_global_template
from services.upload_workflow import (
    MappingChange,
    append_mapping_changes,
    compute_mapping_diff,
    detect_mapping_issues,
    get_workflow_by_review,
    record_mapping_snapshot,
)
from services.workflow_log import append_log
from theme.components import render_page_header, render_section_header
from theme.html_utils import inject_parent_styles

_MAIN = '[data-testid="stMain"]'
_REVIEW_DETAIL_STYLE_ID = "nexus-review-detail-styles"

_TARGET_FIELDS = [
    "partner_code",
    "partner_name",
    "product_category",
    "counterparty_member",
    "counterparty_supplier",
    "amount",
    "currency",
    "period",
    "country",
    "ignore",
]


def _review_detail_styles() -> str:
    return f"""
        {_MAIN} .st-key-review_detail_shell,
        {_MAIN} div[data-testid="stVerticalBlockBorderWrapper"].st-key-review_detail_shell {{
            max-width: 800px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }}

        {_MAIN} .st-key-review_detail_save_row {{
            display: flex !important;
            justify-content: flex-end !important;
            width: 100% !important;
        }}

        {_MAIN} .st-key-review_detail_save_row > div {{
            display: flex !important;
            justify-content: flex-end !important;
            width: 100% !important;
        }}

        {_MAIN} .st-key-review_detail_save_row div[data-testid="stButton"] {{
            display: inline-block !important;
            width: auto !important;
            margin-left: auto !important;
        }}

        {_MAIN} .st-key-review_detail_save_row button,
        {_MAIN} .st-key-review_detail_save_row button[kind="primary"] {{
            background: #000000 !important;
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #000000 !important;
            border-radius: 10px !important;
            transition: background-color 0.2s ease;
        }}

        {_MAIN} .st-key-review_detail_save_row button:hover,
        {_MAIN} .st-key-review_detail_save_row button[kind="primary"]:hover {{
            background: #333333 !important;
            background-color: #333333 !important;
            color: #ffffff !important;
            border-color: #333333 !important;
        }}
    """


def _inject_review_detail_styles() -> None:
    inject_parent_styles(_review_detail_styles(), style_id=_REVIEW_DETAIL_STYLE_ID)


def render(active_page: str = "review_detail") -> None:
    _inject_review_detail_styles()

    with st.container(key="review_detail_shell"):
        render_page_header(subtitle="Manual column mapping and global template save")

        review_id = st.session_state.get("selected_review_id", "")
        if not review_id:
            st.info("No file selected. Open Review Queue first.")
            return

        use_sf = st.session_state.get("use_snowflake", False)
        passcode = st.session_state.get("passcode", "")

        with scoped_connection(passcode, force_demo=not use_sf) as conn:
            detail = get_review_entry(review_id, conn=conn)

        if not detail:
            st.error("Review entry not found.")
            return

        source_columns = detail.get("source_columns", [])
        if not source_columns:
            st.warning("This file has no detected columns.")
            return

        existing_mapping = detail.get("mapping", {}) or {}
        upload_id = detail.get("upload_id", "")
        partner_key = detail.get("partner_key", "")
        wf = get_workflow_by_review(review_id)

        render_section_header(
            "Review Item",
            subtitle=(
                f"{upload_id} — {partner_key} — "
                f"{detail.get('filename', '')}"
            ),
        )
        cap_parts = [
            f"Status: {detail.get('status', 'In review')}",
            f"Validation: {detail.get('validation_source', 'NONE')}",
        ]
        if wf:
            if wf.get("sheet_name"):
                cap_parts.append(f"Sheet: {wf['sheet_name']}")
            if wf.get("truncated"):
                cap_parts.append("Rows truncated for performance")
        st.caption(" | ".join(cap_parts))

        record_mapping_snapshot(review_id, existing_mapping, phase="review_open")

        st.markdown("### Column Mapping Editor")
        right_column_options = _TARGET_FIELDS
        mapping_result: dict[str, str] = {}

        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown("**Left Column (source)**")
        with right_col:
            st.markdown("**Right Column (target)**")

        for source in source_columns:
            lcol, rcol = st.columns(2)
            with lcol:
                st.text_input(
                    f"source_{source}",
                    value=source,
                    disabled=True,
                    label_visibility="collapsed",
                )
            with rcol:
                default_target = existing_mapping.get(source, "ignore")
                default_index = (
                    right_column_options.index(default_target)
                    if default_target in right_column_options
                    else right_column_options.index("ignore")
                )
                selected = st.selectbox(
                    f"target_{source}",
                    right_column_options,
                    index=default_index,
                    key=f"map_{review_id}_{source}",
                    label_visibility="collapsed",
                )
                mapping_result[source] = selected

        st.markdown("---")
        reviewer_note = st.text_area("Reviewer note (optional)", max_chars=500)

        with st.container(key="review_detail_save_row"):
            save_clicked = st.button("Save Template")

        if save_clicked:
            session = get_session()
            reviewer = session.display_name if session else "reviewer"
            wf = get_workflow_by_review(review_id) or {}
            baseline = dict(wf.get("mapping_at_review_open") or existing_mapping)

            diff = compute_mapping_diff(baseline, mapping_result)
            changes = [
                MappingChange(
                    source_column=source,
                    from_target=old,
                    to_target=new,
                    changed_by=reviewer,
                    changed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                )
                for source, old, new in diff
            ]
            append_mapping_changes(
                review_id,
                changes,
                reviewer_note=reviewer_note.strip(),
            )
            record_mapping_snapshot(review_id, mapping_result, phase="final")

            for source, old, new in diff:
                append_log(
                    level="info",
                    action="MAPPING_CHANGED",
                    actor=reviewer,
                    partner_key=partner_key,
                    upload_id=upload_id,
                    review_id=review_id,
                    message=f"'{source}' mapped {old} → {new}",
                )

            issues = detect_mapping_issues(source_columns, mapping_result)
            for issue in issues:
                append_log(
                    level="issue",
                    action="MAPPING_ISSUE",
                    actor=reviewer,
                    partner_key=partner_key,
                    upload_id=upload_id,
                    review_id=review_id,
                    message=issue,
                    meta={"mapping": mapping_result},
                )

            if not diff and not issues:
                append_log(
                    level="warning",
                    action="MAPPING_SAVE",
                    actor=reviewer,
                    partner_key=partner_key,
                    upload_id=upload_id,
                    review_id=review_id,
                    message="Save clicked but no column mapping changes detected.",
                )

            with scoped_connection(passcode, force_demo=not use_sf) as conn:
                save_global_template(
                    review_id=review_id,
                    mapping=mapping_result,
                    reviewer=reviewer,
                    conn=conn,
                )

            append_log(
                level="success",
                action="MAPPING_SAVED",
                actor=reviewer,
                partner_key=partner_key,
                upload_id=upload_id,
                review_id=review_id,
                message="Template saved to Global Memory; review marked Validated.",
                detail=f"{len(diff)} column change(s); {len(issues)} issue(s) logged.",
            )

            if reviewer_note.strip():
                st.caption(f"Note: {reviewer_note.strip()}")
            if issues:
                st.warning(
                    "Mapping saved with issues — see **View Logs** on the supplier dashboard."
                )
            else:
                st.success("Template saved to Global Memory and review item marked Validated.")
            st.session_state.navigate_to = "review_queue"
            st.rerun()

    _inject_review_detail_styles()
