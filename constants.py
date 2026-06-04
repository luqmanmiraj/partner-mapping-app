"""App-wide constants."""

from __future__ import annotations

MAX_UPLOAD_MB = 250
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
# Cap rows processed in-session so large supplier templates (80k+ lines) stay responsive.
MAX_PARSE_ROWS = 20_000


def upload_size_error() -> str:
    return f"File exceeds the {MAX_UPLOAD_MB} MB limit."


def upload_size_help() -> str:
    return f"Accepted: CSV (UTF-8/ISO-8859-1), .xlsx, .xls. Max {MAX_UPLOAD_MB} MB."
