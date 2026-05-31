"""JWT parsing utilities for HubSpot-delegated auth."""

from __future__ import annotations

import jwt


def decode_jwt_unverified(token: str) -> dict:
    """Decode JWT claims without signature verification (Streamlit receives pre-validated token)."""
    return jwt.decode(token, options={"verify_signature": False})


def decode_jwt_verified(token: str, public_key_pem: bytes) -> dict:
    """Verify RS256 JWT from hubspot-mint Lambda."""
    return jwt.decode(
        token,
        public_key_pem,
        algorithms=["RS256"],
        issuer="nexus-partner-mapping",
    )
