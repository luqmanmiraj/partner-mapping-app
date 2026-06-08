"""BRD quarterly closure — preconditions, immutable snapshot."""

from __future__ import annotations

import uuid

import streamlit as st

from auth.snowflake_session import scoped_connection
from services.brd_state import ClosureSnapshot, _now, audit, init_brd_state, list_deposits
from services import snowflake_store


def close_quarter(partner_key: str, quarter: str, *, actor: str = "admin") -> tuple[bool, str]:
    init_brd_state()
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            if snowflake_store.has_in_review_deposits(conn, partner_key, quarter):
                return False, f"Blocked: deposits still In review for {quarter}."
            snapshot_id = snowflake_store.close_quarter_sf(
                conn, partner_key, quarter, actor=actor
            )
            st.session_state.closed_periods.add((partner_key, quarter))
            audit(actor, "CLOSURE", f"{partner_key} {quarter} → {snapshot_id}")
            return True, f"Quarter {quarter} closed. Snapshot {snapshot_id} created (is_billed=TRUE)."

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
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            snowflake_store.record_post_billing_mod_sf(
                conn, partner_key, period, reason, actor=actor
            )

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


def list_post_billing_mods(conn=None) -> list[dict]:
    if conn is not None:
        return snowflake_store.list_post_billing_mods(conn)
    init_brd_state()
    return list(st.session_state.post_billing_mods)
