"""Snowflake connections scoped to the authenticated user's role."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import snowflake.connector

from auth.session import UserSession, get_session
from snowflake_client import (
    DATABASE,
    SnowflakeConnectionError,
    SnowflakeMfaRequired,
    connect,
    connect_with_role,
)


def _cache_key(session: UserSession, passcode: str) -> str:
    role = session.snowflake_role or "ACCOUNTADMIN"
    return f"{role}:{passcode}"


def _get_cached_connection(session: UserSession, passcode: str):
    """Return a live cached connection for this session, or None."""
    import streamlit as st

    key = _cache_key(session, passcode)
    cached = st.session_state.get("_snowflake_conn_cache")
    if not cached or cached.get("key") != key:
        return None
    conn = cached.get("conn")
    if conn is None:
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return conn
    except Exception:
        st.session_state.pop("_snowflake_conn_cache", None)
        try:
            conn.close()
        except Exception:
            pass
        return None


def _store_cached_connection(session: UserSession, passcode: str, conn) -> None:
    import streamlit as st

    st.session_state._snowflake_conn_cache = {
        "key": _cache_key(session, passcode),
        "conn": conn,
    }


@contextmanager
def scoped_connection(
    passcode: str = "",
    *,
    force_demo: bool = False,
) -> Generator[snowflake.connector.SnowflakeConnection | None, None, None]:
    """
    Yield a Snowflake connection scoped to the current user's role.
    Reuses one connection per Streamlit browser session (one MFA per app run).
    Returns None when demo mode is active or connection fails.
    """
    import streamlit as st

    if force_demo or not st.session_state.get("use_snowflake", False):
        yield None
        return

    session = get_session()
    conn = _get_cached_connection(session, passcode)
    owned = False
    try:
        if conn is None:
            if session.snowflake_role and session.snowflake_role not in ("", "ACCOUNTADMIN"):
                conn = connect_with_role(session.snowflake_role, passcode=passcode)
            else:
                conn = connect(passcode=passcode)
            _store_cached_connection(session, passcode, conn)
            owned = True
        yield conn
    except SnowflakeMfaRequired:
        st.session_state.snowflake_error = "Snowflake requires a TOTP passcode."
        st.session_state.pop("_snowflake_conn_cache", None)
        yield None
    except SnowflakeConnectionError as exc:
        st.session_state.snowflake_error = str(exc)
        st.session_state.pop("_snowflake_conn_cache", None)
        yield None
    finally:
        # Keep connection open for reuse; only close if we failed before caching.
        if owned and conn is not None and "_snowflake_conn_cache" not in st.session_state:
            conn.close()


def partner_key_filter(session: UserSession, column: str = "partner_key") -> str:
    """Defense-in-depth filter until Row Access Policies are fully deployed."""
    if session.role_type in ("reviewer", "admin"):
        return "1=1"
    if not session.partner_key:
        return "1=0"
    safe_key = session.partner_key.replace("'", "''")
    return f"{column} = '{safe_key}'"


def schema_fqn(schema: str) -> str:
    return f"{DATABASE}.{schema}"
