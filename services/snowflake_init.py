"""Snowflake mode initialization — auto-enable when credentials exist."""

from __future__ import annotations

import streamlit as st

from snowflake_client import (
    SnowflakeConnectionError,
    SnowflakeMfaRequired,
    credentials_available,
    connect,
)


def init_snowflake_mode() -> None:
    """Enable Snowflake mode when destination credentials are configured."""
    if credentials_available():
        st.session_state.use_snowflake = True
    elif "use_snowflake" not in st.session_state:
        st.session_state.use_snowflake = False
    if "snowflake_error" not in st.session_state:
        st.session_state.snowflake_error = ""


def verify_snowflake_connection(passcode: str = "") -> bool:
    """Test connection; store error message in session on failure."""
    if not st.session_state.get("use_snowflake", False):
        st.session_state.snowflake_error = ""
        return False
    try:
        conn = connect(passcode=passcode)
        conn.close()
        st.session_state.snowflake_error = ""
        return True
    except SnowflakeMfaRequired:
        st.session_state.snowflake_error = "MFA_REQUIRED"
        return False
    except SnowflakeConnectionError as exc:
        st.session_state.snowflake_error = str(exc)
        return False


def _mfa_needed() -> bool:
    err = st.session_state.get("snowflake_error", "")
    return err == "MFA_REQUIRED" or "TOTP" in err or "passcode" in err.lower()


def render_snowflake_mfa_form() -> None:
    """Prominent MFA form on the main page when Snowflake needs a TOTP code."""
    if not st.session_state.get("use_snowflake", False):
        return
    if st.session_state.get("snowflake_verified"):
        return
    # Show form until connected (MFA or first connect attempt)
    if st.session_state.get("snowflake_error") and not _mfa_needed():
        return

    with st.container(border=True):
        st.subheader("Connect to Snowflake")
        st.caption(
            "Your destination account requires a one-time MFA code. "
            "Enter the 6-digit code from your authenticator app (Google Authenticator, etc.)."
        )
        col1, col2 = st.columns([2, 1])
        with col1:
            code = st.text_input(
                "Snowflake MFA code (TOTP)",
                value=st.session_state.get("passcode", ""),
                type="password",
                placeholder="123456",
                key="snowflake_mfa_main",
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("Connect", type="primary", key="snowflake_mfa_connect"):
                st.session_state.passcode = code
                st.session_state.pop("_sf_verified_passcode", None)
                st.session_state.pop("_snowflake_conn_cache", None)
                st.rerun()
        st.caption("You only need to enter this once per app session.")


def render_snowflake_status() -> None:
    """Show connection status banner when Snowflake mode is active."""
    if not st.session_state.get("use_snowflake", False):
        return

    if _mfa_needed() and not st.session_state.get("snowflake_verified"):
        render_snowflake_mfa_form()
        return

    err = st.session_state.get("snowflake_error", "")
    if err and err != "MFA_REQUIRED":
        st.warning(f"Snowflake: {err}")
    elif st.session_state.get("snowflake_verified"):
        from snowflake_client import load_dest_config

        try:
            cfg = load_dest_config(passcode=st.session_state.get("passcode", ""))
            account = cfg["dest_account"]
        except Exception:
            account = "destination"
        st.caption(f"Connected to Snowflake — {account} (PM_PROD).")
