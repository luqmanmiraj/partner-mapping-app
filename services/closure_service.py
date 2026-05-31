"""BRD quarterly closure — preconditions, immutable snapshot."""

from __future__ import annotations

import uuid

import streamlit as st

from services.brd_state import (
    ClosureSnapshot,
    _now,
    audit,
    init_brd_state,
    list_deposits,
)


def close_quarter(partner_key: str, quarter: str, *, actor: str = "admin") -> tuple[bool, str]:
    init_brd_state()

    for dep in list_deposits(partner_key):
        if quarter in dep.period and dep.status == "In review":
            return False, f"Blocked: deposit {dep.upload_id} still In review for {quarter}."

    snapshot_id = f"SNAP-{uuid.uuid4().hex[:8].upper()}"
    snap = ClosureSnapshot(
        snapshot_id=snapshot_id,
        partner_key=partner_key,
        quarter_label=quarter,
        created_by=actor,
    )
    st.session_state.snapshots.append(snap)
    st.session_state.closed_periods.add((partner_key, quarter))
    audit(actor, "CLOSURE", f"{partner_key} {quarter} → {snapshot_id}")
    return True, f"Quarter {quarter} closed. Snapshot {snapshot_id} created (is_billed=TRUE)."


def record_post_billing_mod(partner_key: str, period: str, reason: str, *, actor: str) -> None:
    init_brd_state()

    st.session_state.post_billing_mods.insert(
        0,
        {
            "partner_key": partner_key,
            "period": period,
            "reason": reason,
            "author": actor,
            "timestamp": _now(),
        },
    )
    audit(actor, "POST_BILLING_MOD", f"{partner_key} {period}: {reason}")
