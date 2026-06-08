"""BRD admin — onboarding, decommission, calibration, system config."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from services.brd_state import PartnerRecord, audit, get_partner, init_brd_state
from services.file_parser import parse_upload
from services import snowflake_store


def activate_partner(
    partner_key: str,
    hubspot_company_id: str,
    declarant_type: str = "supplier",
    default_currency: str = "EUR",
    *,
    actor: str = "admin",
) -> str:
    init_brd_state()
    st.session_state.partners[partner_key] = PartnerRecord(
        partner_key=partner_key,
        declarant_type=declarant_type,
        hubspot_company_id=hubspot_company_id,
        is_active=True,
        default_currency=default_currency,
    )

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            snowflake_store.activate_partner_sf(conn, partner_key, actor=actor)

    audit(actor, "ONBOARD", f"{partner_key} role PM_PARTNER_{partner_key}")
    return f"Partner {partner_key} activated. Snowflake role PM_PARTNER_{partner_key}."


def deactivate_partner(partner_key: str, *, actor: str = "admin") -> str:
    p = get_partner(partner_key)
    if not p:
        return "Partner not found."
    p.is_active = False
    init_brd_state()
    st.session_state.partners[partner_key] = p

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            snowflake_store.deactivate_partner_sf(conn, partner_key)

    audit(actor, "DECOMMISSION", partner_key)
    return f"Partner {partner_key} deactivated. Access revoked; audit record retained."


def calibrate_partner(
    partner_key: str,
    file1_bytes: bytes,
    file1_name: str,
    file2_bytes: bytes,
    file2_name: str,
    *,
    actor: str = "admin",
) -> str:
    p1 = parse_upload(file1_name, file1_bytes)
    p2 = parse_upload(file2_name, file2_bytes)
    if not p1.success or not p2.success:
        return "Both type files must parse successfully."

    cols1 = set(p1.lines[0].keys()) if p1.lines else set()
    cols2 = set(p2.lines[0].keys()) if p2.lines else set()
    stable = cols1 == cols2 and len(cols1) > 0
    column_mapping = {c: c for c in cols1}

    init_brd_state()
    p = get_partner(partner_key) or PartnerRecord(partner_key, "supplier")
    p.calibration_stable = stable
    p.column_mapping = column_mapping
    st.session_state.partners[partner_key] = p

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            snowflake_store.save_calibration_template(
                conn,
                partner_key=partner_key,
                source_columns=list(cols1),
                column_mapping=column_mapping,
                is_stable=stable,
                actor=actor,
            )

    audit(actor, "CALIBRATION", f"{partner_key} stable={stable} cols={list(cols1)}")
    if stable:
        return f"Calibration stable — {len(cols1)} columns mapped for {partner_key} (saved to Snowflake)."
    return "Structure differs between file 1 and file 2 — adjust mapping manually before activation."


def update_system_config(
    confidence: float,
    info_pct: float,
    alert_pct: float,
    *,
    actor: str = "admin",
) -> str:
    init_brd_state()
    old = dict(st.session_state.system_config)
    st.session_state.system_config.update(
        {
            "confidence_threshold": confidence,
            "discrepancy_info_pct": info_pct,
            "discrepancy_alert_pct": alert_pct,
        }
    )

    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            snowflake_store.update_system_config_sf(
                conn,
                confidence=confidence,
                info_pct=info_pct,
                alert_pct=alert_pct,
                actor=actor,
            )

    audit(actor, "CONFIG_CHANGE", f"{old} → {st.session_state.system_config}")
    return "System configuration updated."


def list_partner_keys(conn=None) -> list[str]:
    if conn is not None:
        return [p["partner_key"] for p in snowflake_store.load_active_partners(conn)]
    init_brd_state()
    return list(st.session_state.partners.keys())
