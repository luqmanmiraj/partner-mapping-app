"""HubSpot iframe JWT bridge — uses HubSpot auth service layer."""

from __future__ import annotations

import os

import streamlit as st

from services.hubspot_auth_service import (
    extract_jwt_token,
    mint_jwt_for_company,
    token_is_not_expired,
)


def extract_jwt_from_request() -> str | None:
    """Read JWT from query params (HubSpot CMS server-side injection)."""
    return extract_jwt_token(st.query_params, st.session_state)


def mint_jwt_from_hubspot(company_id: str) -> dict | None:
    """Call hubspot-mint Lambda to obtain a scoped JWT."""
    try:
        return mint_jwt_for_company(company_id, timeout=10)
    except Exception as exc:
        st.sidebar.error(f"JWT mint failed: {exc}")
        return None


def apply_jwt_to_session(token: str) -> bool:
    """Parse JWT claims and store in session. Returns False if token is expired."""
    try:
        if not token_is_not_expired(token):
            st.error("Session expired. Please refresh the HubSpot page.")
            return False
        st.session_state.jwt_token = token
        st.session_state.pop("user_session", None)
        return True
    except Exception as exc:
        st.error(f"Invalid authentication token: {exc}")
        return False


def init_hubspot_auth() -> None:
    """On app load: pick up JWT from iframe URL or mint in dev."""
    if st.session_state.get("jwt_initialized"):
        return

    token = extract_jwt_from_request()
    if token:
        apply_jwt_to_session(token)
    elif os.environ.get("HUBSPOT_COMPANY_ID"):
        result = mint_jwt_from_hubspot(os.environ["HUBSPOT_COMPANY_ID"])
        if result and result.get("token"):
            apply_jwt_to_session(result["token"])

    st.session_state.jwt_initialized = True
