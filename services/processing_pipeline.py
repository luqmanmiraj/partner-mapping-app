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

def _mock_eur(amount: float, currency: str) -> tuple[float, bool]:
    rates = {"EUR": 1.0, "USD": 0.92, "GBP": 1.17, "PLN": 0.23, "CHF": 1.05}
    rate = rates.get(currency, 1.0)
    return round(amount * rate, 2), currency != "EUR"


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
        audit(partner_key, "UPLOAD_REJECTED", parsed.error)
        return False, "", parsed.error

    if not parsed.lines:
        return False, "", "File contains no data lines."

    upload_id = f"DEP-{uuid.uuid4().hex[:8].upper()}"
    auto, review, rejected = 0, 0, 0
    reasons: list[str] = []
    local_total = 0.0

    for row in parsed.lines[:5000]:
        amount_raw = next((v for k, v in row.items() if k.lower() in ("amount", "total", "turnover", "value")), "0")
        try:
            amount = float(str(amount_raw).replace(",", "").replace("€", "").strip() or 0)
        except ValueError:
            amount = 0.0
        if amount < 0:
            pass  # BR-DECL-07 negative amounts valid
        local_total += amount

    source_columns = list(parsed.lines[0].keys())

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

        create_review_entry(
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
        record_post_billing_mod(partner_key, period, comment or "Corrective deposit on closed period", actor=partner_key)

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
        rejected=rejected,
        rejection_reasons=reasons,
        local_total=local_total,
        eur_total=eur_total,
        pending_final_rate=pending_rate,
        submitted_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        is_corrective=is_corrective,
        supersedes_upload_id=supersedes_upload_id,
        line_count=parsed.row_count,
        reconciled_csv="line,amount_eur,status\n" + "\n".join(
            f"{i},{local_total/max(parsed.row_count,1):.2f},validated" for i in range(min(5, parsed.row_count))
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

    if status == "Validated":
        return True, upload_id, "File validated using memory template and stored."
    return True, upload_id, "File uploaded and routed to reviewer for manual mapping."
