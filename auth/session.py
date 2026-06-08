"""Auth session management — JWT from HubSpot iframe or dev mock."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

import streamlit as st

RoleType = Literal["partner", "reviewer", "admin"]

MOCK_COMPANY_MAP: dict[str, dict] = {
    "11111111": {
        "partner_key": "MEYLE",
        "type": "supplier",
        "display_name": "Meyle GmbH",
        "default_currency": "EUR",
        "is_active": True,
    },
    "22222222": {
        "partner_key": "NISSENS",
        "type": "supplier",
        "display_name": "Nissens",
        "default_currency": "EUR",
        "is_active": True,
    },
    "33333333": {
        "partner_key": "TMD",
        "type": "supplier",
        "display_name": "TMD Friction",
        "default_currency": "EUR",
        "is_active": True,
    },
    "44444444": {
        "partner_key": "HELLA",
        "type": "supplier",
        "display_name": "HELLA",
        "default_currency": "EUR",
        "is_active": True,
    },
    "55555555": {
        "partner_key": "BREMBO",
        "type": "supplier",
        "display_name": "Brembo",
        "default_currency": "EUR",
        "is_active": True,
    },
    "66666601": {
        "partner_key": "MEMBER_DE_001",
        "type": "member",
        "display_name": "Member DE Pilot",
        "default_currency": "EUR",
        "is_active": True,
    },
    "66666602": {
        "partner_key": "MEMBER_FR_001",
        "type": "member",
        "display_name": "Member FR Pilot",
        "default_currency": "EUR",
        "is_active": True,
    },
    "66666603": {
        "partner_key": "MEMBER_ES_001",
        "type": "member",
        "display_name": "Member ES Pilot",
        "default_currency": "EUR",
        "is_active": True,
    },
    "66666604": {
        "partner_key": "MEMBER_IT_001",
        "type": "member",
        "display_name": "Member IT Pilot",
        "default_currency": "EUR",
        "is_active": True,
    },
    "66666605": {
        "partner_key": "MEMBER_PL_001",
        "type": "member",
        "display_name": "Member PL Pilot",
        "default_currency": "PLN",
        "is_active": True,
    },
}


@dataclass
class UserSession:
    role_type: RoleType
    partner_key: str = ""
    declarant_type: str = ""
    display_name: str = "User"
    snowflake_role: str = ""
    default_currency: str = "EUR"
    is_active: bool = True
    jwt_token: str = ""
    hubspot_company_id: str = ""

    @property
    def role_label(self) -> str:
        if self.role_type == "partner":
            return f"Partner ({self.declarant_type})"
        if self.role_type == "reviewer":
            return "Reviewer"
        return "Admin"

    @property
    def counterparty_label(self) -> str:
        return "Members" if self.declarant_type == "supplier" else "Suppliers"


def _parse_jwt_from_request() -> dict | None:
    """Read JWT from query params (HubSpot iframe injection) or session."""
    from auth.jwt_utils import decode_jwt_unverified

    token = st.query_params.get("jwt") or st.session_state.get("jwt_token")
    if not token:
        return None
    try:
        claims = decode_jwt_unverified(token)
        st.session_state.jwt_token = token
        return claims
    except Exception:
        return None


def _session_from_jwt(claims: dict) -> UserSession:
    partner_key = claims.get("sub", "")
    declarant_type = claims.get("type", "supplier")
    role = claims.get("role", f"PM_PARTNER_{partner_key}")
    return UserSession(
        role_type="partner",
        partner_key=partner_key,
        declarant_type=declarant_type,
        display_name=partner_key.replace("_", " ").title(),
        snowflake_role=role,
        jwt_token=st.session_state.get("jwt_token", ""),
        is_active=claims.get("is_active", True),
        default_currency=claims.get("default_currency", "EUR"),
    )


def _session_from_dev_mock() -> UserSession:
    app_role = st.session_state.get("app_role", "partner")
    if app_role == "reviewer":
        return UserSession(
            role_type="reviewer",
            display_name="Internal Reviewer",
            snowflake_role="PM_REVIEWER",
        )
    if app_role == "admin":
        return UserSession(
            role_type="admin",
            display_name="Internal Admin",
            snowflake_role="PM_ADMIN",
        )

    company_id = st.session_state.get("hubspot_company_id", "11111111")
    record = MOCK_COMPANY_MAP.get(company_id, MOCK_COMPANY_MAP["11111111"])
    return UserSession(
        role_type="partner",
        partner_key=record["partner_key"],
        declarant_type=record["type"],
        display_name=record["display_name"],
        snowflake_role=f"PM_PARTNER_{record['partner_key']}",
        default_currency=record.get("default_currency", "EUR"),
        is_active=record.get("is_active", True),
        hubspot_company_id=company_id,
    )


def init_session() -> UserSession | None:
    """Initialize auth session. Returns None if partner is inactive."""
    from services.brd_state import init_brd_state, partner_is_active

    init_brd_state()

    if "user_session" not in st.session_state:
        app_role = st.session_state.get("app_role", "partner")
        if app_role in ("reviewer", "admin"):
            session = _session_from_dev_mock()
        else:
            claims = _parse_jwt_from_request()
            if claims:
                session = _session_from_jwt(claims)
            else:
                session = _session_from_dev_mock()
        st.session_state.user_session = session

    session: UserSession = st.session_state.user_session
    if session.role_type == "partner" and session.partner_key:
        if not partner_is_active(session.partner_key):
            session.is_active = False
    if session.role_type == "partner" and not session.is_active:
        return None
    return session


def get_session() -> UserSession:
    session = st.session_state.get("user_session")
    if session is None:
        session = init_session() or UserSession(role_type="partner", display_name="Guest")
        st.session_state.user_session = session
    return session


def is_partner() -> bool:
    return get_session().role_type == "partner"


def is_reviewer() -> bool:
    return get_session().role_type == "reviewer"


def is_admin() -> bool:
    return get_session().role_type == "admin"


def mint_dev_jwt(company_id: str) -> str | None:
    """Mint a dev JWT via hubspot-mint mock mode (optional)."""
    mint_url = os.environ.get("HUBSPOT_MINT_URL", "")
    if not mint_url:
        return None
    import json
    import urllib.request

    req = urllib.request.Request(
        mint_url,
        data=json.dumps({"hubspot_company_id": company_id}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = json.loads(resp.read().decode())
            return body.get("token")
    except Exception:
        return None
