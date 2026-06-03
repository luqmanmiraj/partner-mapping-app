"""In-memory BRD domain state (demo until Snowflake/API wired)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import streamlit as st

DEPOSIT_STATUSES = (
    "Pending processing",
    "In review",
    "Validated",
    "Partially rejected",
    "Rejected",
    "Superseded",
)


@dataclass
class PartnerRecord:
    partner_key: str
    declarant_type: str
    hubspot_company_id: str = ""
    is_active: bool = True
    default_currency: str = "EUR"
    calibration_stable: bool = False
    column_mapping: dict[str, str] = field(default_factory=dict)


@dataclass
class DepositRecord:
    upload_id: str
    partner_key: str
    period: str
    currency: str
    filename: str
    comment: str
    status: str = "Pending processing"
    auto_validated: int = 0
    in_review: int = 0
    rejected: int = 0
    rejection_reasons: list[str] = field(default_factory=list)
    local_total: float = 0.0
    eur_total: float = 0.0
    pending_final_rate: bool = False
    submitted_at: str = ""
    is_corrective: bool = False
    supersedes_upload_id: str = ""
    line_count: int = 0
    reconciled_csv: str = ""


@dataclass
class MappingProposal:
    proposal_id: str
    partner_key: str
    upload_id: str
    dimension: str
    source_value: str
    proposed_target: str
    confidence_score: float
    status: str = "Pending"
    reviewer_comment: str = ""
    tags: list[str] = field(default_factory=list)
    memory_scope: str = "LOCAL"


@dataclass
class ClosureSnapshot:
    snapshot_id: str
    partner_key: str
    quarter_label: str
    is_billed: bool = True
    created_at: str = ""
    created_by: str = "admin"


@dataclass
class AuditEntry:
    timestamp: str
    actor: str
    action: str
    detail: str


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def init_brd_state() -> None:
    if "brd_initialized" in st.session_state:
        return
    st.session_state.brd_initialized = True
    st.session_state.deposits: dict[str, DepositRecord] = {}
    st.session_state.proposals: dict[str, MappingProposal] = {}
    st.session_state.local_memory: dict[str, dict[str, str]] = {}
    st.session_state.global_memory: dict[str, str] = {}
    st.session_state.closed_periods: set[tuple[str, str]] = set()
    st.session_state.snapshots: list[ClosureSnapshot] = []
    st.session_state.post_billing_mods: list[dict[str, Any]] = []
    st.session_state.system_config = {
        "confidence_threshold": 0.9,
        "discrepancy_info_pct": 1.0,
        "discrepancy_alert_pct": 10.0,
    }
    st.session_state.audit_log: list[AuditEntry] = []
    st.session_state.partners: dict[str, PartnerRecord] = {
        "MEYLE": PartnerRecord("MEYLE", "supplier", "11111111", True, "EUR"),
        "HELLA": PartnerRecord("HELLA", "supplier", "44444444", True, "EUR"),
        "TMD": PartnerRecord("TMD", "supplier", "33333333", True, "EUR"),
        "MEMBER_DE_001": PartnerRecord("MEMBER_DE_001", "member", "66666601", True, "EUR"),
    }
    _seed_demo_deposits()
    _seed_demo_proposals()


def _seed_demo_proposals() -> None:
    from data import demo_fixtures

    for _, row in demo_fixtures.review_queue().iterrows():
        p = MappingProposal(
            proposal_id=str(row["Proposal ID"]),
            partner_key=str(row["Partner"]),
            upload_id="DEP-DEMO",
            dimension=str(row["Dimension"]),
            source_value=str(row["Source Value"]),
            proposed_target=str(row["Proposed Target"]),
            confidence_score=float(row["Confidence"]),
            status=str(row["Status"]),
        )
        st.session_state.proposals[p.proposal_id] = p


def _seed_demo_deposits() -> None:
    from auth.session import UserSession
    from data import demo_fixtures

    session = UserSession(
        role_type="partner",
        partner_key="MEYLE",
        declarant_type="supplier",
        display_name="Meyle",
    )
    for _, row in demo_fixtures.deposit_history(session).iterrows():
        dep = DepositRecord(
            upload_id=str(row["Deposit ID"]),
            partner_key="MEYLE",
            period=str(row["Period"]),
            currency=str(row["Currency"]),
            filename="demo.xlsx",
            comment="",
            status=str(row["Status"]),
            line_count=int(row["Lines"]),
            submitted_at="2026-04-28 14:32 UTC",
            auto_validated=1180 if row["Status"] == "Validated" else 0,
            in_review=42 if row["Status"] == "In review" else 0,
            rejected=18 if "reject" in str(row["Status"]).lower() else 0,
            local_total=2_450_000.0,
            eur_total=2_450_000.0,
            reconciled_csv="line,amount,status\n1,100,validated\n",
        )
        st.session_state.deposits[dep.upload_id] = dep


def audit(actor: str, action: str, detail: str) -> None:
    init_brd_state()
    st.session_state.audit_log.insert(
        0,
        AuditEntry(timestamp=_now(), actor=actor, action=action, detail=detail),
    )


def get_partner(partner_key: str) -> PartnerRecord | None:
    init_brd_state()
    return st.session_state.partners.get(partner_key)


def partner_is_active(partner_key: str) -> bool:
    p = get_partner(partner_key)
    return p.is_active if p else True


def list_deposits(partner_key: str) -> list[DepositRecord]:
    init_brd_state()
    return sorted(
        [d for d in st.session_state.deposits.values() if d.partner_key == partner_key],
        key=lambda d: d.submitted_at,
        reverse=True,
    )


def get_deposit(upload_id: str) -> DepositRecord | None:
    init_brd_state()
    return st.session_state.deposits.get(upload_id)


def save_deposit(dep: DepositRecord) -> None:
    init_brd_state()
    st.session_state.deposits[dep.upload_id] = dep


def is_period_closed(partner_key: str, period: str) -> bool:
    init_brd_state()
    return (partner_key, period) in st.session_state.closed_periods


def list_proposals(**filters) -> list[MappingProposal]:
    init_brd_state()
    items = list(st.session_state.proposals.values())
    if "partner" in filters and filters["partner"] != "All":
        items = [p for p in items if p.partner_key == filters["partner"]]
    if "dimension" in filters and filters["dimension"] != "All":
        items = [p for p in items if p.dimension == filters["dimension"]]
    if "max_confidence" in filters:
        items = [p for p in items if p.confidence_score <= filters["max_confidence"]]
    return sorted(items, key=lambda p: p.confidence_score)


def get_proposal(proposal_id: str) -> MappingProposal | None:
    init_brd_state()
    return st.session_state.proposals.get(proposal_id)


def save_proposal(p: MappingProposal) -> None:
    init_brd_state()
    st.session_state.proposals[p.proposal_id] = p


def get_config() -> dict:
    init_brd_state()
    return st.session_state.system_config
