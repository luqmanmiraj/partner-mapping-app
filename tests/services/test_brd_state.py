"""Unit tests for services.brd_state."""

from __future__ import annotations

from services.brd_state import (
    DepositRecord,
    MappingProposal,
    get_deposit,
    get_partner,
    list_deposits,
    list_proposals,
    partner_is_active,
    save_deposit,
    save_proposal,
)


def test_init_seeds_demo_partners_and_deposits(brd_state) -> None:
    assert get_partner("MEYLE") is not None
    assert get_partner("MEMBER_DE_001").declarant_type == "member"
    deposits = list_deposits("MEYLE")
    assert len(deposits) >= 1


def test_save_deposit_and_retrieve(brd_state) -> None:
    dep = DepositRecord(
        upload_id="DEP-TEST-001",
        partner_key="MEYLE",
        period="Q3-2026",
        currency="EUR",
        filename="test.csv",
        comment="pytest",
        status="Pending processing",
        line_count=10,
    )
    save_deposit(dep)
    loaded = get_deposit("DEP-TEST-001")
    assert loaded is not None
    assert loaded.period == "Q3-2026"
    assert loaded.line_count == 10


def test_list_proposals_filters_by_partner(brd_state) -> None:
    save_proposal(
        MappingProposal(
            proposal_id="P-TEST-1",
            partner_key="HELLA",
            upload_id="DEP-X",
            dimension="Brand",
            source_value="X",
            proposed_target="Y",
            confidence_score=0.5,
        )
    )
    hella = list_proposals(partner="HELLA")
    assert any(p.proposal_id == "P-TEST-1" for p in hella)
    meyle = list_proposals(partner="MEYLE")
    assert all(p.proposal_id != "P-TEST-1" for p in meyle)


def test_partner_is_active_defaults_true_for_unknown(brd_state) -> None:
    assert partner_is_active("UNKNOWN_PARTNER") is True
    assert partner_is_active("MEYLE") is True
