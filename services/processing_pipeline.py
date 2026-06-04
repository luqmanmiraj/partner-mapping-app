"""BRD Steps 2–7 — mapping, validation, currency, notifications (demo)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import streamlit as st

from auth.snowflake_session import scoped_connection
from data.notification_fixtures import NotificationItem, get_notifications
from services.brd_state import (
    DepositRecord,
    audit,
    init_brd_state,
    save_deposit,
)
from services.file_parser import parse_upload
from services.memory_store import create_review_entry, resolve_template
from services.upload_workflow import UploadWorkflow, save_workflow
from services.workflow_log import append_log


def _mock_eur(amount: float, currency: str) -> tuple[float, bool]:
    rates = {"EUR": 1.0, "USD": 0.92, "GBP": 1.17, "PLN": 0.23, "CHF": 1.05}
    rate = rates.get(currency, 1.0)
    return round(amount * rate, 2), currency != "EUR"


def _amount_column_keys(row: dict) -> list[str]:
    keys: list[str] = []
    for key in row:
        low = key.lower()
        if any(
            token in low
            for token in (
                "amount",
                "total",
                "turnover",
                "sales",
                "netsales",
                "gross",
                "value",
                "volume",
            )
        ):
            keys.append(key)
    return keys


def _sum_row_amounts(lines: list[dict]) -> float:
    total = 0.0
    for row in lines[:5000]:
        keys = _amount_column_keys(row)
        raw = next((row[k] for k in keys if str(row.get(k, "")).strip()), "0")
        try:
            amount = float(str(raw).replace(",", "").replace("€", "").strip() or 0)
        except ValueError:
            amount = 0.0
        total += amount
    return total


def process_upload(
    *,
    file_bytes: bytes,
    filename: str,
    period: str,
    currency: str,
    comment: str,
    partner_key: str,
    is_corrective: bool = False,
    supersedes_upload_id: str = "",
) -> tuple[bool, str, str]:
    """Returns (success, upload_id, message)."""
    init_brd_state()

    parsed = parse_upload(filename, file_bytes)
    if not parsed.success:
        append_log(
            level="error",
            action="UPLOAD_REJECTED",
            actor=partner_key,
            partner_key=partner_key,
            message="Upload rejected — file could not be parsed.",
            detail=parsed.error,
            meta={"filename": filename},
        )
        audit(partner_key, "UPLOAD_REJECTED", parsed.error)
        return False, "", parsed.error

    if not parsed.lines:
        msg = "File contains no data lines."
        append_log(
            level="error",
            action="UPLOAD_REJECTED",
            actor=partner_key,
            partner_key=partner_key,
            message=msg,
            detail=filename,
        )
        return False, "", msg

    upload_id = f"DEP-{uuid.uuid4().hex[:8].upper()}"
    local_total = _sum_row_amounts(parsed.lines)
    source_columns = list(parsed.lines[0].keys())

    append_log(
        level="info",
        action="UPLOAD_PARSED",
        actor=partner_key,
        partner_key=partner_key,
        upload_id=upload_id,
        message=f"Parsed {parsed.row_count:,} rows from {filename}.",
        detail=f"Sheet: {parsed.sheet_name or 'n/a'}",
        meta={
            "columns": len(source_columns),
            "truncated": parsed.truncated,
            "warnings": parsed.warnings or [],
        },
    )
    for warning in parsed.warnings or []:
        append_log(
            level="warning",
            action="UPLOAD_PARSE_WARNING",
            actor=partner_key,
            partner_key=partner_key,
            upload_id=upload_id,
            message=warning,
        )

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        resolved = resolve_template(partner_key, source_columns, conn=conn)
        if resolved:
            status = "Validated"
            auto = parsed.row_count
            review = 0
            validation_source = str(resolved.get("scope", "GLOBAL"))
            mapping = dict(resolved.get("mapping", {}))
        else:
            status = "In review"
            auto = 0
            review = parsed.row_count
            validation_source = "NONE"
            mapping = {}

        review_id = create_review_entry(
            upload_id=upload_id,
            partner_key=partner_key,
            filename=filename,
            period=period,
            source_columns=source_columns,
            status=status,
            validation_source=validation_source,
            mapping=mapping,
            conn=conn,
        )

    save_workflow(
        UploadWorkflow(
            upload_id=upload_id,
            review_id=review_id,
            partner_key=partner_key,
            filename=filename,
            period=period,
            currency=currency,
            status=status,
            validation_source=validation_source,
            source_columns=source_columns,
            sheet_name=parsed.sheet_name,
            row_count=parsed.row_count,
            truncated=bool(parsed.truncated),
            mapping_at_upload=dict(mapping),
            mapping_at_review_open=dict(mapping),
        )
    )

    append_log(
        level="success" if status == "Validated" else "info",
        action="UPLOAD_PROCESSED",
        actor=partner_key,
        partner_key=partner_key,
        upload_id=upload_id,
        review_id=review_id,
        message=f"Upload {upload_id} — status {status}.",
        detail=f"Validation: {validation_source}",
        meta={"row_count": parsed.row_count, "column_count": len(source_columns)},
    )

    eur_total, pending_rate = _mock_eur(local_total, currency)

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
            partner_key,
            period,
            comment or "Corrective deposit on closed period",
            actor=partner_key,
        )

    dep = DepositRecord(
        upload_id=upload_id,
        partner_key=partner_key,
        period=period,
        currency=currency,
        filename=filename,
        comment=comment,
        status=status,
        auto_validated=auto,
        in_review=review,
        rejected=0,
        rejection_reasons=[],
        local_total=local_total,
        eur_total=eur_total,
        pending_final_rate=pending_rate,
        submitted_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        is_corrective=is_corrective,
        supersedes_upload_id=supersedes_upload_id,
        line_count=parsed.row_count,
        reconciled_csv="line,amount_eur,status\n"
        + "\n".join(
            f"{i},{local_total / max(parsed.row_count, 1):.2f},validated"
            for i in range(min(5, parsed.row_count))
        ),
    )
    save_deposit(dep)
    audit(
        partner_key,
        "UPLOAD_PROCESSED",
        f"{upload_id} status={status} validation={validation_source} lines={parsed.row_count}",
    )

    get_notifications().insert(
        0,
        NotificationItem(
            id=f"n-{upload_id}",
            category="Declaration",
            message=f"Processing complete for {period}: {status}.",
            date="Today",
            notification_type="deposit",
            is_read=False,
        ),
    )

    msg = (
        "File validated using memory template and stored."
        if status == "Validated"
        else "File uploaded and routed to reviewer for manual mapping."
    )
    if parsed.truncated:
        msg += f" Note: only first {parsed.row_count:,} rows were processed (large file)."
    return True, upload_id, msg
