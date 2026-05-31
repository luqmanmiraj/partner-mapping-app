"""Demo fixtures aligned with BRD statuses — used when Snowflake schemas are empty."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from auth.session import UserSession


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def deposit_history(session: UserSession) -> pd.DataFrame:
    cp_label = session.counterparty_label
    return pd.DataFrame(
        [
            {
                "Deposit ID": "DEP-2026-0042",
                "Period": "April 2026",
                "Submitted": "2026-04-28 14:32",
                "Currency": session.default_currency,
                "Lines": 1240,
                "Status": "Validated",
            },
            {
                "Deposit ID": "DEP-2026-0038",
                "Period": "March 2026",
                "Submitted": "2026-03-25 09:15",
                "Currency": session.default_currency,
                "Lines": 1180,
                "Status": "Validated",
            },
            {
                "Deposit ID": "DEP-2026-0031",
                "Period": "February 2026",
                "Submitted": "2026-02-22 16:48",
                "Currency": session.default_currency,
                "Lines": 45,
                "Status": "In review",
            },
            {
                "Deposit ID": "DEP-2026-0025",
                "Period": "January 2026",
                "Submitted": "2026-01-20 11:02",
                "Currency": session.default_currency,
                "Lines": 890,
                "Status": "Partially rejected",
            },
            {
                "Deposit ID": "DEP-2025-0199",
                "Period": "Q4 2025",
                "Submitted": "2025-12-18 08:55",
                "Currency": session.default_currency,
                "Lines": 3200,
                "Status": "Superseded",
            },
        ]
    )


def deposit_detail(deposit_id: str, session: UserSession) -> dict:
    cp = session.counterparty_label.rstrip("s")
    return {
        "deposit_id": deposit_id,
        "period": "April 2026",
        "status": "Validated",
        "submitted_at": _now(),
        "currency": session.default_currency,
        "auto_validated": 1180,
        "in_review": 42,
        "rejected": 18,
        "rejection_reasons": [
            f"Unknown {cp.lower()} code: GARAGE_XYZ_99",
            "Invalid date format on line 445",
            "Negative amount without credit note reference (line 892)",
        ],
        "local_total": 2_450_000.0,
        "eur_total": 2_450_000.0,
    }


def financial_dashboard(session: UserSession) -> dict:
    cp_label = session.counterparty_label
    monthly = pd.DataFrame(
        {
            "period": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
            "turnover_local": [180000, 195000, 210000, 225000, 240000, 255000, 270000, 285000],
            "turnover_eur": [180000, 195000, 210000, 225000, 240000, 255000, 270000, 285000],
            "turnover_n1": [170000, 185000, 200000, 215000, 230000, 245000, 260000, 275000],
        }
    )
    top_counterparties = pd.DataFrame(
        {
            cp_label.rstrip("s"): [
                "Garage Dupont SARL",
                "Auto Parts Berlin GmbH",
                "Madrid Motor SL",
                "Milano Ricambi SpA",
                "Warsaw Auto Center",
                "Stockholm Bil AB",
                "Oslo Verksted AS",
                "København Auto",
                "Praha Parts s.r.o.",
                "Budapest Autó Kft.",
            ],
            "Country": ["FR", "DE", "ES", "IT", "PL", "SE", "NO", "DK", "CZ", "HU"],
            "Turnover (EUR)": [
                "€420K", "€385K", "€340K", "€310K", "€275K",
                "€250K", "€230K", "€210K", "€195K", "€180K",
            ],
            "Share": ["18%", "16%", "14%", "13%", "12%", "11%", "10%", "9%", "8%", "7%"],
        }
    )
    return {
        "overview_cards": [
            {
                "label": "Cumulated Turnover (EUR)",
                "value": "€2.45M",
                "delta": "+12.4% vs N-1",
                "positive": True,
            },
            {
                "label": f"Cumulated Turnover ({session.default_currency})",
                "value": "€2.45M",
                "delta": "YTD 2026",
                "positive": True,
            },
            {
                "label": "Validated Lines",
                "value": "9,842",
                "delta": "98.2% auto-validated",
                "positive": True,
            },
            {
                "label": f"Top {cp_label}",
                "value": "10",
                "delta": "Shown in EUR",
                "positive": True,
            },
        ],
        "monthly": monthly,
        "top_counterparties": top_counterparties,
        "last_updated": _now(),
        "period_closed": False,
    }


def review_queue() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Proposal ID": "MAP-8842",
                "Partner": "MEYLE",
                "Dimension": "product_category",
                "Source Value": "Oil filter XYZ 500ml",
                "Proposed Target": "Oil Filter (GA-00123)",
                "Confidence": "0.72",
                "Status": "Pending",
            },
            {
                "Proposal ID": "MAP-8843",
                "Partner": "HELLA",
                "Dimension": "counterparty_member",
                "Source Value": "Garage Dupont SARL",
                "Proposed Target": "myID-00012345",
                "Confidence": "0.68",
                "Status": "Pending",
            },
            {
                "Proposal ID": "MAP-8844",
                "Partner": "TMD",
                "Dimension": "product_category",
                "Source Value": "GenArt 82 Brake pad set",
                "Proposed Target": "Brake Pads (GA-00456)",
                "Confidence": "0.81",
                "Status": "Pending",
            },
            {
                "Proposal ID": "MAP-8845",
                "Partner": "MEMBER_DE_001",
                "Dimension": "counterparty_supplier",
                "Source Value": "BOSCH AUTO FR",
                "Proposed Target": "SUP-00007",
                "Confidence": "0.55",
                "Status": "Pending",
            },
        ]
    )


def review_detail(proposal_id: str) -> dict:
    return {
        "proposal_id": proposal_id,
        "partner": "MEYLE",
        "dimension": "product_category",
        "source_value": "Oil filter XYZ 500ml",
        "proposed_target": "Oil Filter (GA-00123)",
        "confidence": 0.72,
        "context": {
            "Country": "DE",
            "Partner type": "supplier",
            "Similar cases": 3,
            "Previous mapping": "None (LOCAL)",
        },
        "tags": [],
    }


def overlap_cases() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Case ID": "OVL-001",
                "Period": "Q1 2026",
                "Supplier": "HELLA",
                "Parent": "HELLA Group",
                "Parent Amount": "€1,250,000",
                "Descendants Sum": "€1,249,999.99",
                "Gap (EUR)": "€0.01",
                "Gap (%)": "0.00%",
                "Status": "Auto-resolved",
            },
            {
                "Case ID": "OVL-002",
                "Period": "Q1 2026",
                "Supplier": "TMD",
                "Parent": "TMD Holdings",
                "Parent Amount": "€890,000",
                "Descendants Sum": "€845,000",
                "Gap (EUR)": "€45,000",
                "Gap (%)": "5.06%",
                "Status": "Investigation pending",
            },
        ]
    )


def discrepancy_matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Supplier": "MEYLE",
                "Member": "Member DE Pilot",
                "Turnover (Supplier)": "€420,000",
                "Turnover (Member)": "€415,800",
                "Abs. Gap": "€4,200",
                "Rel. Gap": "1.0%",
                "Tag": "Acceptable",
            },
            {
                "Supplier": "HELLA",
                "Member": "Member FR Pilot",
                "Turnover (Supplier)": "€680,000",
                "Turnover (Member)": "€580,000",
                "Abs. Gap": "€100,000",
                "Rel. Gap": "14.7%",
                "Tag": "Investigation pending",
            },
        ]
    )


CLOSED_PERIODS = {"Q4 2025", "December 2025"}
