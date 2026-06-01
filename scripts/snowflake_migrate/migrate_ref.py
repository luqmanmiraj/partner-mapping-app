"""Snowflake destination constants and session helpers (standalone app copy).

In the full nexus monorepo this module lives under scripts/snowflake_migrate/.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import snowflake.connector
from dotenv import load_dotenv

DATABASE = os.environ.get("SNOWFLAKE_DEST_DATABASE", "PM_PROD")
SCHEMA = os.environ.get("SNOWFLAKE_DEST_SCHEMA", "REF")

_ENV_PATH = Path(__file__).resolve().parent / ".env.migrate"


def normalize_account(account: str) -> str:
    """Return a Snowflake connector account identifier."""
    value = account.strip()
    if not value:
        return value
    value = re.sub(r"\.snowflakecomputing\.com$", "", value, flags=re.IGNORECASE)
    if "." in value and "-" not in value:
        org, name = value.split(".", 1)
        if org and name:
            value = f"{org}-{name}"
    return value


def activate_session(
    conn: snowflake.connector.SnowflakeConnection,
    *,
    warehouse: str,
    label: str,
    role: str,
    database: str,
    schema: str,
) -> None:
    """Set role, warehouse, database, and schema on an open connection."""
    del label  # reserved for logging in the monorepo tool
    cur = conn.cursor()
    try:
        cur.execute(f"USE ROLE {role}")
        cur.execute(f"USE WAREHOUSE {warehouse}")
        cur.execute(f"USE DATABASE {database}")
        cur.execute(f"USE SCHEMA {schema}")
    finally:
        cur.close()


def load_config(*, env_path: Path | None = None) -> dict[str, Any]:
    """Load SNOWFLAKE_* variables from .env.migrate (monorepo migrate CLI compatibility)."""
    path = env_path or _ENV_PATH
    if path.exists():
        load_dotenv(path, interpolate=False, override=True)
    return dict(os.environ)
