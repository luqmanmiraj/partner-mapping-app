"""Admin cockpit — BRD functionality (minimal UI)."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from services.admin_service import (
    activate_partner,
    calibrate_partner,
    deactivate_partner,
    update_system_config,
)
from services.brd_state import get_config, init_brd_state
from services.closure_service import close_quarter
from theme.components import render_data_table, render_page_header, render_section_header


def render_calibration(active_page: str = "admin_calibration") -> None:
    render_page_header("Admin", subtitle="Partner file calibration (BRD Admin > Calibration)")
    render_section_header("Upload 2 type files")
    partner_key = st.text_input("Partner key", value="MEYLE")
    f1 = st.file_uploader("Type file 1", type=["csv", "xlsx", "xls"], key="cal1")
    f2 = st.file_uploader("Type file 2", type=["csv", "xlsx", "xls"], key="cal2")
    if st.button("Run calibration") and f1 and f2:
        msg = calibrate_partner(partner_key, f1.getvalue(), f1.name, f2.getvalue(), f2.name)
        st.success(msg)


def render_onboarding(active_page: str = "admin_onboarding") -> None:
    render_page_header("Admin", subtitle="Partner onboarding")
    partner_key = st.text_input("Partner key", placeholder="MEYLE")
    hubspot_id = st.text_input("HubSpot company ID")
    decl_type = st.selectbox("Type", ["supplier", "member"])
    currency = st.selectbox("Default currency", ["EUR", "USD", "GBP", "PLN"])
    if st.button("Activate partner", type="primary"):
        st.success(activate_partner(partner_key, hubspot_id, decl_type, currency))


def render_decommission(active_page: str = "admin_decommission") -> None:
    render_page_header("Admin", subtitle="Partner decommissioning")
    partner_key = st.selectbox("Partner", ["MEYLE", "HELLA", "TMD", "MEMBER_DE_001"])
    if st.button("Deactivate partner"):
        st.warning(deactivate_partner(partner_key))


def render_closure(active_page: str = "admin_closure") -> None:
    render_page_header("Admin", subtitle="Quarterly accounting closure")
    partner = st.selectbox("Partner", ["MEYLE", "HELLA", "TMD", "MEMBER_DE_001"])
    quarter = st.selectbox("Quarter", ["Q1 2026", "Q4 2025"])
    confirm = st.checkbox("I confirm this action is irreversible")
    if st.button("Close quarter", type="primary") and confirm:
        ok, msg = close_quarter(partner, quarter)
        st.success(msg) if ok else st.error(msg)


def render_system_config(active_page: str = "admin_config") -> None:
    render_page_header("Admin", subtitle="System configuration")
    cfg = get_config()
    conf = st.slider("Confidence threshold (auto-validate)", 0.5, 1.0, float(cfg["confidence_threshold"]), 0.05)
    info = st.number_input("Discrepancy info %", value=float(cfg["discrepancy_info_pct"]))
    alert = st.number_input("Discrepancy alert %", value=float(cfg["discrepancy_alert_pct"]))
    if st.button("Save configuration"):
        st.success(update_system_config(conf, info, alert))


def render_post_closure_audit(active_page: str = "admin_audit") -> None:
    render_page_header("Admin", subtitle="Post-closure audit")
    init_brd_state()
    if st.session_state.post_billing_mods:
        render_data_table(
            __import__("pandas").DataFrame(st.session_state.post_billing_mods),
            columns=["partner_key", "period", "reason", "author", "timestamp"],
        )
    else:
        st.info("No post-closure modifications recorded.")
    if st.session_state.snapshots:
        st.subheader("Accounting snapshots")
        for s in st.session_state.snapshots:
            st.write(f"- {s.snapshot_id}: {s.partner_key} {s.quarter_label} (billed={s.is_billed})")
