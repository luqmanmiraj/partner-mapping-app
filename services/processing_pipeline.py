"""BRD Steps 2–7 — mapping, validation, currency, notifications (demo)."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

from data.notification_fixtures import NotificationItem, get_notifications
from services.brd_state import (
    DepositRecord,
    MappingProposal,
    audit,
    get_config,
    get_partner,
    init_brd_state,
    save_deposit,
    save_proposal,
)
from services.file_parser import parse_upload

import streamlit as st


def _mock_eur(amount: float, currency: str) -> tuple[float, bool]:
    rates = {"EUR": 1.0, "USD": 0.92, "GBP": 1.17, "PLN": 0.23, "CHF": 1.05}
    rate = rates.get(currency, 1.0)
    return round(amount * rate, 2), currency != "EUR" and random.random() < 0.1


def _resolve_confidence(partner_key: str, source: str, dimension: str) -> float:
    init_brd_state()
    local = st.session_state.local_memory.get(partner_key, {})
    key = f"{dimension}:{source}"
    if key in local:
        return 1.0
    if key in st.session_state.global_memory:
        return 0.95
    return round(random.uniform(0.55, 0.98), 2)


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
    threshold = get_config()["confidence_threshold"]

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

    for i, row in enumerate(parsed.lines[:5000]):
        amount_raw = next((v for k, v in row.items() if k.lower() in ("amount", "total", "turnover", "value")), "0")
        try:
            amount = float(str(amount_raw).replace(",", "").replace("€", "").strip() or 0)
        except ValueError:
            amount = 0.0
        if amount < 0:
            pass  # BR-DECL-07 negative amounts valid
        local_total += amount

        for dim in ("product_category", "counterparty_member", "counterparty_supplier"):
            source = str(row.get(list(row.keys())[0], f"line_{i}"))
            conf = _resolve_confidence(partner_key, source, dim)
            if conf >= threshold:
                auto += 1
            else:
                review += 1
                pid = f"MAP-{uuid.uuid4().hex[:6].upper()}"
                save_proposal(
                    MappingProposal(
                        proposal_id=pid,
                        partner_key=partner_key,
                        upload_id=upload_id,
                        dimension=dim,
                        source_value=source[:200],
                        proposed_target=f"TARGET-{dim[:3].upper()}-{i}",
                        confidence_score=conf,
                    )
                )

    if rejected == len(parsed.lines) and len(parsed.lines) > 0:
        status = "Rejected"
    elif review > 0 and auto > 0:
        status = "Partially rejected" if rejected else "In review"
    elif review > 0:
        status = "In review"
    else:
        status = "Validated"

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
    audit(partner_key, "UPLOAD_PROCESSED", f"{upload_id} status={status} lines={parsed.row_count}")

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

    return True, upload_id, f"File received and processed. Status: {status}."
