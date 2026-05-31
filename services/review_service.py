"""BRD review actions — validate, modify, reject, bulk, memory write-back."""

from __future__ import annotations

import streamlit as st

from services.brd_state import MappingProposal, audit, get_proposal, init_brd_state, save_proposal


def validate_proposal(
    proposal_id: str,
    *,
    actor: str = "reviewer",
    modified_target: str | None = None,
    memory_scope: str = "LOCAL",
    comment: str = "",
    tags: list[str] | None = None,
) -> str:
    p = get_proposal(proposal_id)
    if not p:
        return "Proposal not found."
    target = modified_target or p.proposed_target
    p.status = "Validated"
    p.proposed_target = target
    p.reviewer_comment = comment
    p.tags = tags or []
    p.memory_scope = memory_scope
    save_proposal(p)
    _write_memory(p, target, memory_scope)
    audit(actor, "REVIEW_VALIDATE", f"{proposal_id} → {target} ({memory_scope})")
    return "Validated."


def reject_proposal(proposal_id: str, reason: str, *, actor: str = "reviewer") -> str:
    if not reason.strip():
        return "Rejection reason required."
    p = get_proposal(proposal_id)
    if not p:
        return "Proposal not found."
    p.status = "Rejected"
    p.reviewer_comment = reason
    save_proposal(p)
    audit(actor, "REVIEW_REJECT", f"{proposal_id}: {reason}")
    return "Rejected."


def bulk_action(proposal_ids: list[str], action: str, *, actor: str = "reviewer") -> str:
    count = 0
    for pid in proposal_ids:
        if action == "Validate all as-is":
            validate_proposal(pid, actor=actor)
            count += 1
        elif action == "Reject all":
            reject_proposal(pid, "Bulk rejection", actor=actor)
            count += 1
    return f"Applied to {count} proposal(s)."


def _write_memory(p: "MappingProposal", target: str, scope: str) -> None:
    init_brd_state()
    key = f"{p.dimension}:{p.source_value}"
    if scope == "LOCAL":
        st.session_state.local_memory.setdefault(p.partner_key, {})[key] = target
    else:
        st.session_state.global_memory[key] = target
