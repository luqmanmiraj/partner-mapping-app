"""HubSpot auth service: JWT extraction, validation, and mint API calls."""

from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any

from auth.jwt_utils import decode_jwt_unverified


def hubspot_mint_url() -> str:
    """Resolve configured mint endpoint (empty when not configured)."""
    return os.environ.get(
        "HUBSPOT_MINT_URL",
        os.environ.get("VITE_HUBSPOT_MINT_URL", ""),
    )


def extract_jwt_token(query_params: Any, session_state: Any) -> str | None:
    """Extract JWT from query params first, then session fallback."""
    token = query_params.get("jwt")
    if token:
        return token
    return session_state.get("jwt_token")


def mint_jwt_for_company(company_id: str, *, timeout: int = 10) -> dict[str, Any] | None:
    """Call hubspot-mint backend and return parsed JSON body."""
    mint_url = hubspot_mint_url()
    if not mint_url:
        return None

    req = urllib.request.Request(
        mint_url,
        data=json.dumps({"hubspot_company_id": company_id}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def token_is_not_expired(token: str) -> bool:
    """Check exp claim without signature verification (same trust model as app)."""
    claims = decode_jwt_unverified(token)
    return float(claims.get("exp", 0)) >= time.time()
