"""Unit tests for services.review_service."""

from __future__ import annotations

from services.brd_state import MappingProposal, save_proposal
from services.review_service import bulk_action, reject_proposal, validate_proposal


def _proposal(proposal_id: str = "P-REV-1") -> MappingProposal:
    return MappingProposal(
        proposal_id=proposal_id,
        partner_key="MEYLE",
        upload_id="DEP-1",
        dimension="Brand",
        source_value="Bosch",
        proposed_target="BOSCH_GMBH",
        confidence_score=0.82,
    )


def test_validate_proposal_updates_status_and_memory(brd_state) -> None:
    save_proposal(_proposal())
    msg = validate_proposal("P-REV-1", memory_scope="LOCAL", comment="ok")
    assert msg == "Validated."

    import streamlit as st

    memory = st.session_state.local_memory["MEYLE"]
    assert memory["Brand:Bosch"] == "BOSCH_GMBH"


def test_reject_proposal_requires_reason(brd_state) -> None:
    save_proposal(_proposal("P-REV-2"))
    assert reject_proposal("P-REV-2", "   ") == "Rejection reason required."
    assert reject_proposal("P-REV-2", "Invalid mapping") == "Rejected."


def test_bulk_action_validate_all(brd_state) -> None:
    save_proposal(_proposal("P-BULK-1"))
    save_proposal(_proposal("P-BULK-2"))
    result = bulk_action(["P-BULK-1", "P-BULK-2"], "Validate all as-is")
    assert "2 proposal" in result
