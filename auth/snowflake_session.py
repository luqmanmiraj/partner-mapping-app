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


@contextmanager
def scoped_connection(
    passcode: str = "",
    *,
    force_demo: bool = False,
) -> Generator[snowflake.connector.SnowflakeConnection | None, None, None]:
    """
    Yield a Snowflake connection scoped to the current user's role.
    Returns None when demo mode is active or connection fails.
    """
    import streamlit as st

    if force_demo or not st.session_state.get("use_snowflake", False):
        yield None
        return

    session = get_session()
    conn = None
    try:
        if session.snowflake_role and session.snowflake_role not in ("", "ACCOUNTADMIN"):
            conn = connect_with_role(session.snowflake_role, passcode=passcode)
        else:
            conn = connect(passcode=passcode)
        yield conn
    except (SnowflakeConnectionError, SnowflakeMfaRequired):
        yield None
    finally:
        if conn is not None:
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
