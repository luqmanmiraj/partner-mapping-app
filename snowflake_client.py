"""Snowflake connection for the partner dashboard (destination account from .env.migrate)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd
import snowflake.connector
from snowflake.connector.errors import DatabaseError

APP_ROOT = Path(__file__).resolve().parent


def _migrate_dir_candidates() -> tuple[Path, ...]:
    return (
        APP_ROOT.parent / "scripts" / "snowflake_migrate",
        APP_ROOT / "scripts" / "snowflake_migrate",
    )


def _resolve_migrate_dir() -> Path:
    """Prefer the migrate folder that has credentials, then monorepo layout."""
    with_env = [p for p in _migrate_dir_candidates() if (p / ".env.migrate").exists()]
    if with_env:
        return with_env[0]
    for path in _migrate_dir_candidates():
        if (path / "migrate_ref.py").exists():
            return path
    return _migrate_dir_candidates()[0]


MIGRATE_DIR = _resolve_migrate_dir()
if str(MIGRATE_DIR) not in sys.path:
    sys.path.insert(0, str(MIGRATE_DIR))

from migrate_ref import (  # noqa: E402
    DATABASE,
    SCHEMA,
    activate_session,
    normalize_account,
)
from dotenv import load_dotenv

_ENV_CANDIDATES = tuple(
    p / ".env.migrate"
    for p in _migrate_dir_candidates()
) + (APP_ROOT / ".env.migrate",)
ENV_PATH = next((p for p in _ENV_CANDIDATES if p.exists()), _ENV_CANDIDATES[0])


def credentials_available() -> bool:
    """True when destination Snowflake credentials are configured."""
    if not ENV_PATH.exists():
        return False
    load_dotenv(ENV_PATH, interpolate=False, override=True)
    import os

    return all(os.environ.get(k) for k in ("SNOWFLAKE_DEST_ACCOUNT", "SNOWFLAKE_DEST_USER", "SNOWFLAKE_DEST_PASSWORD"))


class SnowflakeConnectionError(Exception):
    """Raised when the dashboard cannot connect to Snowflake."""


class SnowflakeMfaRequired(SnowflakeConnectionError):
    """Raised when TOTP MFA is required."""


def _mfa_kwargs(passcode: str) -> dict[str, str]:
    if not passcode:
        return {}
    return {"passcode": passcode, "passcode_in_password": False}


def load_dest_config(*, passcode: str = "") -> dict[str, str]:
    if not ENV_PATH.exists():
        raise SnowflakeConnectionError(
            f"Missing {ENV_PATH}. Copy .env.migrate.example and set destination credentials."
        )
    load_dotenv(ENV_PATH, interpolate=False, override=True)

    required = [
        "SNOWFLAKE_DEST_ACCOUNT",
        "SNOWFLAKE_DEST_USER",
        "SNOWFLAKE_DEST_PASSWORD",
    ]
    missing = [key for key in required if not __import__("os").environ.get(key)]
    if missing:
        raise SnowflakeConnectionError(f"Missing env vars in .env.migrate: {', '.join(missing)}")

    import os

    def _strip_quotes(value: str) -> str:
        v = value.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
            return v[1:-1]
        return v

    return {
        "dest_account": normalize_account(os.environ["SNOWFLAKE_DEST_ACCOUNT"]),
        "dest_user": os.environ["SNOWFLAKE_DEST_USER"].strip(),
        "dest_password": _strip_quotes(os.environ["SNOWFLAKE_DEST_PASSWORD"]),
        "dest_role": os.environ.get("SNOWFLAKE_DEST_ROLE", "ACCOUNTADMIN"),
        "dest_warehouse": os.environ.get("SNOWFLAKE_DEST_WAREHOUSE", "PM_WH"),
        "dest_passcode": passcode or os.environ.get("SNOWFLAKE_DEST_PASSCODE", ""),
    }


def connect(passcode: str = "", *, schema: str | None = None) -> snowflake.connector.SnowflakeConnection:
    return connect_with_role(None, passcode=passcode, schema=schema or SCHEMA)


def connect_with_role(
    role: str | None,
    passcode: str = "",
    *,
    schema: str = SCHEMA,
) -> snowflake.connector.SnowflakeConnection:
    cfg = load_dest_config(passcode=passcode)
    effective_role = role or cfg["dest_role"]
    try:
        conn = snowflake.connector.connect(
            account=cfg["dest_account"],
            user=cfg["dest_user"],
            password=cfg["dest_password"],
            role=effective_role,
            warehouse=cfg["dest_warehouse"],
            **_mfa_kwargs(cfg["dest_passcode"]),
        )
        activate_session(
            conn,
            warehouse=cfg["dest_warehouse"],
            label="dest",
            role=effective_role,
            database=DATABASE,
            schema=schema,
        )
        return conn
    except DatabaseError as exc:
        msg = str(exc)
        if "MFA" in msg or "TOTP" in msg or "passcode" in msg.lower():
            raise SnowflakeMfaRequired(
                "Destination Snowflake account requires a TOTP passcode."
            ) from exc
        raise SnowflakeConnectionError(msg) from exc


def query_df(conn: snowflake.connector.SnowflakeConnection, sql: str) -> pd.DataFrame:
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [col[0] for col in (cur.description or [])]
        return pd.DataFrame(rows, columns=columns)
    finally:
        cur.close()


def table_columns(conn: snowflake.connector.SnowflakeConnection, table: str) -> dict[str, str]:
    cur = conn.cursor()
    try:
        cur.execute(f"SHOW COLUMNS IN TABLE {DATABASE}.{SCHEMA}.{table}")
        return {row[2].lower(): row[2] for row in cur.fetchall()}
    finally:
        cur.close()


def pick_column(columns: dict[str, str], *candidates: str) -> str | None:
    for name in candidates:
        if name.lower() in columns:
            return columns[name.lower()]
    return None
