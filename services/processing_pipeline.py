"""BRD Steps 1–7 — full pipeline via pipeline_engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.notification_fixtures import NotificationItem, get_notifications
from services.brd_state import DepositRecord, audit, init_brd_state, save_deposit
from services.file_parser import parse_upload
from services.memory_store import create_review_entry
from services.pipeline_engine import run_pipeline
from services.pipeline_log import PipelineLogger


def process_upload(
    *,
    file_bytes: bytes,
    filename: str,
    period: str,
    currency: str,
    comment: str,
    partner_key: str,
    declarant_type: str = "supplier",
    is_corrective: bool = False,
    supersedes_upload_id: str = "",
) -> tuple[bool, str, str]:
    """Returns (success, upload_id, message)."""
    init_brd_state()
    upload_id = f"DEP-{uuid.uuid4().hex[:8].upper()}"
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        plog = PipelineLogger(upload_id=upload_id, partner_key=partner_key, conn=conn)

        plog.log(1, "Parsing", "started", f"File received: {filename} ({len(file_bytes):,} bytes)")
        parsed = parse_upload(filename, file_bytes)
        if not parsed.success:
            plog.log(1, "Parsing", "failed", parsed.error)
            audit(partner_key, "UPLOAD_REJECTED", parsed.error)
            return False, "", parsed.error
        if not parsed.lines:
            plog.log(1, "Parsing", "failed", "File contains no data lines.")
            return False, "", "File contains no data lines."

        enc = getattr(parsed, "encoding", "utf-8")
        sep = getattr(parsed, "separator", ",")
        cols = list(parsed.lines[0].keys())
        plog.log(
            1,
            "Parsing",
            "completed",
            f"encoding={enc}, separator={sep!r}, rows={parsed.row_count}, columns={cols}",
            snowflake_target="STAGING.PARSED_LINE",
        )

        from services.brd_state import get_config

        threshold = get_config()["confidence_threshold"]
        result = run_pipeline(
            conn,
            upload_id=upload_id,
            partner_key=partner_key,
            declarant_type=declarant_type,
            filename=filename,
            file_bytes=file_bytes,
            period=period,
            currency=currency,
            comment=comment,
            parsed=parsed,
            threshold=threshold,
            is_corrective=is_corrective,
            supersedes_upload_id=supersedes_upload_id,
            plog=plog,
        )

        review_id = create_review_entry(
            upload_id=upload_id,
            partner_key=partner_key,
            filename=filename,
            period=period,
            source_columns=cols,
            status=result.status,
            validation_source=result.validation_source,
            mapping=result.column_mapping,
            conn=conn,
        )
        init_brd_state()
        if review_id in st.session_state.review_entries:
            st.session_state.review_entries[review_id]["pending_proposals"] = result.in_review

        get_notifications().insert(
            0,
            NotificationItem(
                id=f"n-{upload_id}",
                category="Declaration",
                message=f"Processing complete for {period}: {result.status}.",
                date="Today",
                notification_type="deposit",
                is_read=False,
            ),
        )

    if is_corrective and supersedes_upload_id:
        from services.brd_state import get_deposit

        old = get_deposit(supersedes_upload_id)
        if old:
            old.status = "Superseded"
            save_deposit(old)
            audit(partner_key, "SUPERSEDE", f"{supersedes_upload_id} → {upload_id}")

    from services.brd_state import is_period_closed
    from services.closure_service import record_post_billing_mod

    if is_corrective and is_period_closed(partner_key, period):
        record_post_billing_mod(
            partner_key, period, comment or "Corrective deposit on closed period", actor=partner_key
        )

    dep = DepositRecord(
        upload_id=upload_id,
        partner_key=partner_key,
        period=period,
        currency=currency,
        filename=filename,
        comment=comment,
        status=result.status,
        auto_validated=result.auto_validated,
        in_review=result.in_review,
        rejected=result.rejected,
        rejection_reasons=result.rejection_reasons,
        local_total=result.local_total,
        eur_total=result.eur_total,
        pending_final_rate=result.pending_final_rate,
        submitted_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        is_corrective=is_corrective,
        supersedes_upload_id=supersedes_upload_id,
        line_count=len(result.line_results),
        reconciled_csv="line,amount_eur,status\n"
        + "\n".join(
            f"{lr.line_number},{lr.amount_eur:.2f},"
            f"{'validated' if lr.fully_validated else 'in_review'}"
            for lr in result.line_results[:20]
        ),
    )
    save_deposit(dep)
    audit(
        partner_key,
        "UPLOAD_PROCESSED",
        f"{upload_id} status={result.status} auto={result.auto_validated} review={result.in_review}",
    )
    st.session_state.last_pipeline_upload_id = upload_id

    if result.status == "Validated":
        return (
            True,
            upload_id,
            f"Validated ({result.auto_validated} lines) → APP.VALIDATED_LINE + OUTPUT.BUSINESS_VIEW. "
            f"Trace in Admin → Pipeline Monitor.",
        )
    return (
        True,
        upload_id,
        f"In review ({result.in_review} lines) → APP.MAPPING_PROPOSAL. Trace in Admin → Pipeline Monitor.",
    )
