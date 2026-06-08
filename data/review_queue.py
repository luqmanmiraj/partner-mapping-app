"""Review queue data — BRD store + optional Snowflake."""

from __future__ import annotations

import pandas as pd

# Re-export QA loaders for backwards compatibility
from data.qa_loaders import load_discrepancy_matrix, load_overlap_cases

__all__ = [
    "load_review_queue",
    "load_review_detail",
    "load_overlap_cases",
    "load_discrepancy_matrix",
]


def load_review_queue(conn=None, **filters) -> pd.DataFrame:
    from services.brd_state import get_config, init_brd_state, list_proposals

    init_brd_state()
    threshold = get_config()["confidence_threshold"]
    max_conf = filters.get("max_confidence", threshold)

    if conn is not None:
        from auth.snowflake_session import schema_fqn
        from snowflake_client import query_df

        try:
            return query_df(
                conn,
                f"""
                SELECT proposal_id AS "Proposal ID", partner_key AS "Partner",
                       dimension AS "Dimension", source_value AS "Source Value",
                       proposed_target AS "Proposed Target",
                       ROUND(confidence_score, 2) AS "Confidence", status AS "Status"
                FROM {schema_fqn("APP")}.MAPPING_PROPOSAL
                WHERE confidence_score < {threshold} AND status = 'Pending'
                ORDER BY confidence_score ASC LIMIT 100
                """,
            )
        except Exception:
            pass

    items = list_proposals(
        partner=filters.get("partner_filter", "All"),
        dimension=filters.get("dimension_filter", "All"),
        max_confidence=max_conf,
    )
    if not items:
        from data import demo_fixtures

        return demo_fixtures.review_queue()

    return pd.DataFrame(
        [
            {
                "Proposal ID": p.proposal_id,
                "Partner": p.partner_key,
                "Dimension": p.dimension,
                "Source Value": p.source_value,
                "Proposed Target": p.proposed_target,
                "Confidence": f"{p.confidence_score:.2f}",
                "Status": p.status,
            }
            for p in items
        ]
    )


def load_review_detail(proposal_id: str, conn=None) -> dict:
    from services.brd_state import get_proposal, init_brd_state
    from services import snowflake_store

    init_brd_state()
    if conn is not None:
        row = snowflake_store.get_proposal(conn, proposal_id)
        if row:
            return {
                "proposal_id": row["proposal_id"],
                "partner": row["partner_key"],
                "dimension": row["dimension"],
                "source_value": row["source_value"],
                "proposed_target": row["proposed_target"],
                "confidence": row["confidence_score"],
                "context": {"Upload ID": row["upload_id"], "Status": row["status"]},
                "tags": row.get("tags") or [],
            }
    p = get_proposal(proposal_id)
    if p:
        return {
            "proposal_id": p.proposal_id,
            "partner": p.partner_key,
            "dimension": p.dimension,
            "source_value": p.source_value,
            "proposed_target": p.proposed_target,
            "confidence": p.confidence_score,
            "context": {"Upload ID": p.upload_id, "Status": p.status},
            "tags": p.tags,
        }
    from data import demo_fixtures

    return demo_fixtures.review_detail(proposal_id)
