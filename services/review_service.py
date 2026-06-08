"""BRD review actions — validate, modify, reject, bulk, memory write-back."""

from __future__ import annotations

import streamlit as st

from auth.snowflake_session import scoped_connection
from services.brd_state import MappingProposal, audit, get_proposal, init_brd_state, save_proposal
from services import snowflake_store


def _get_proposal_any(proposal_id: str, conn=None) -> MappingProposal | None:
    p = get_proposal(proposal_id)
    if p:
        return p
    if conn is not None:
        row = snowflake_store.get_proposal(conn, proposal_id)
        if row:
            return MappingProposal(
                proposal_id=row["proposal_id"],
                upload_id=row["upload_id"],
                partner_key=row["partner_key"],
                dimension=row["dimension"],
                source_value=row["source_value"],
                proposed_target=row["proposed_target"],
                confidence_score=row["confidence_score"],
                status=row["status"],
                memory_scope=row.get("memory_scope") or "LOCAL",
                reviewer_comment=row.get("reviewer_comment") or "",
                tags=row.get("tags") or [],
            )
    return None


def validate_proposal(
    proposal_id: str,
    *,
    actor: str = "reviewer",
    modified_target: str | None = None,
    memory_scope: str = "LOCAL",
    comment: str = "",
    tags: list[str] | None = None,
) -> str:
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        p = _get_proposal_any(proposal_id, conn=conn)
        if not p:
            return "Proposal not found."
        target = modified_target or p.proposed_target
        p.status = "Validated"
        p.proposed_target = target
        p.reviewer_comment = comment
        p.tags = tags or []
        p.memory_scope = memory_scope
        save_proposal(p)

        if conn is not None:
            snowflake_store.update_proposal(
                conn,
                proposal_id,
                status="Validated",
                proposed_target=target,
                memory_scope=memory_scope,
                reviewer_comment=comment,
                tags=tags,
            )
            snowflake_store.save_value_memory(
                conn,
                partner_key=p.partner_key,
                dimension=p.dimension,
                source_value=p.source_value,
                target_value=target,
                scope=memory_scope,
            )
        else:
            _write_memory_session(p, target, memory_scope)

    audit(actor, "REVIEW_VALIDATE", f"{proposal_id} → {target} ({memory_scope})")
    return "Validated."


def reject_proposal(proposal_id: str, reason: str, *, actor: str = "reviewer") -> str:
    if not reason.strip():
        return "Rejection reason required."
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")

    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        p = _get_proposal_any(proposal_id, conn=conn)
        if not p:
            return "Proposal not found."
        p.status = "Rejected"
        p.reviewer_comment = reason
        save_proposal(p)
        if conn is not None:
            snowflake_store.update_proposal(
                conn, proposal_id, status="Rejected", reviewer_comment=reason
            )

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


def save_qa_tag(
    case_id: str,
    case_type: str,
    resolution: str,
    tag: str,
    *,
    actor: str = "reviewer",
) -> None:
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            snowflake_store.save_qa_resolution(
                conn, case_id=case_id, case_type=case_type, resolution=resolution, tag=tag, actor=actor
            )
    audit(actor, "QA_RESOLUTION", f"{case_id}: {resolution} / {tag}")


def _write_memory_session(p: MappingProposal, target: str, scope: str) -> None:
    init_brd_state()
    key = f"{p.dimension}:{p.source_value}"
    if scope == "LOCAL":
        st.session_state.local_memory.setdefault(p.partner_key, {})[key] = target
    else:
        st.session_state.global_memory[key] = target
