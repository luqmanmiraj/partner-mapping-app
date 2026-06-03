"""HubSpot iframe JWT bridge — server-side token handling (BR-ISO-04)."""

from __future__ import annotations

import json
import os
import urllib.request

import streamlit as st

from auth.jwt_utils import decode_jwt_unverified


def extract_jwt_from_request() -> str | None:
    """Read JWT from query params (HubSpot CMS server-side injection)."""
    token = st.query_params.get("jwt")
    if token:
        return token
    return st.session_state.get("jwt_token")


def mint_jwt_from_hubspot(company_id: str) -> dict | None:
    """Call hubspot-mint Lambda to obtain a scoped JWT."""
    mint_url = os.environ.get(
        "HUBSPOT_MINT_URL",
        os.environ.get("VITE_HUBSPOT_MINT_URL", ""),
    )
    if not mint_url:
        return None

    req = urllib.request.Request(
        mint_url,
        data=json.dumps({"hubspot_company_id": company_id}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as exc:
        st.sidebar.error(f"JWT mint failed: {exc}")
        return None


def apply_jwt_to_session(token: str) -> bool:
    """Parse JWT claims and store in session. Returns False if token is expired."""
    try:
        claims = decode_jwt_unverified(token)
        import time

        if claims.get("exp", 0) < time.time():
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
