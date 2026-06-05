"""HubSpot OAuth service for login URL creation and callback exchange."""

from __future__ import annotations

import json
import os
import secrets
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

_APP_ROOT = Path(__file__).resolve().parent.parent
_OAUTH_STATE_FILE = _APP_ROOT / ".streamlit" / "hubspot_oauth_state.json"


def oauth_enabled() -> bool:
    return bool(
        os.environ.get("HUBSPOT_CLIENT_ID")
        and os.environ.get("HUBSPOT_CLIENT_SECRET")
        and os.environ.get("HUBSPOT_REDIRECT_URI")
    )


def oauth_scopes() -> str:
    raw = os.environ.get(
        "HUBSPOT_OAUTH_SCOPES",
        "oauth crm.objects.companies.read",
    )
    return raw.replace("+", " ").strip()


def redirect_uri() -> str:
    return os.environ.get("HUBSPOT_REDIRECT_URI", "")


def persist_oauth_state(state: str) -> None:
    """Persist OAuth state across HubSpot redirect (Streamlit session may reset)."""
    _OAUTH_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _OAUTH_STATE_FILE.write_text(json.dumps({"state": state}), encoding="utf-8")


def validate_oauth_state(state: str | None) -> bool:
    if not state:
        return False
    if not _OAUTH_STATE_FILE.is_file():
        return True
    try:
        saved = json.loads(_OAUTH_STATE_FILE.read_text(encoding="utf-8"))
        return saved.get("state") == state
    except (json.JSONDecodeError, OSError):
        return True


def clear_oauth_state() -> None:
    try:
        _OAUTH_STATE_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def build_authorize_url(*, state: str) -> str:
    persist_oauth_state(state)
    params = {
        "client_id": os.environ.get("HUBSPOT_CLIENT_ID", ""),
        "redirect_uri": redirect_uri(),
        "scope": oauth_scopes(),
        "state": state,
    }
    return "https://app.hubspot.com/oauth/authorize?" + urllib.parse.urlencode(params)


def new_state() -> str:
    return secrets.token_urlsafe(24)


def exchange_code_for_tokens(code: str) -> dict[str, Any]:
    payload = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "client_id": os.environ.get("HUBSPOT_CLIENT_ID", ""),
            "client_secret": os.environ.get("HUBSPOT_CLIENT_SECRET", ""),
            "redirect_uri": redirect_uri(),
            "code": code,
        }
    ).encode()

    req = urllib.request.Request(
        "https://api.hubapi.com/oauth/v1/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_access_token_metadata(access_token: str) -> dict[str, Any]:
    url = f"https://api.hubapi.com/oauth/v1/access-tokens/{access_token}"
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def process_oauth_callback(code: str, state: str | None) -> dict[str, Any]:
    """
    Exchange OAuth code and return profile payload for the callback screen.

    Raises ValueError on state/token errors; urllib errors on network/API failures.
    """
    if not validate_oauth_state(state):
        raise ValueError("OAuth state mismatch. Please sign in again.")

    token_payload = exchange_code_for_tokens(code)
    access_token = token_payload.get("access_token", "")
    if not access_token:
        raise ValueError("HubSpot did not return an access token.")

    meta = fetch_access_token_metadata(access_token)
    clear_oauth_state()

    company_id = os.environ.get("HUBSPOT_COMPANY_ID", "")
    profile = {
        "user": meta.get("user"),
        "hub_id": meta.get("hub_id"),
        "app_id": meta.get("app_id"),
        "hub_domain": meta.get("hub_domain"),
        "company_id": company_id,
        "scopes": meta.get("scopes", []),
    }
    return {
        "profile": profile,
        "access_token": access_token,
    }
