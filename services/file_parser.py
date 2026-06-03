"""BRD Step 1 — file parsing (encoding, separator, lines)."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass

import pandas as pd

from constants import MAX_UPLOAD_BYTES, upload_size_error


@dataclass
class ParseResult:
    success: bool
    lines: list[dict]
    encoding: str = "utf-8"
    separator: str = ","
    error: str = ""
    row_count: int = 0


def _detect_encoding(raw: bytes) -> str:
    for enc in ("utf-8", "iso-8859-1", "windows-1252"):
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    return "utf-8"


def _detect_separator(text: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=",;\t")
        return dialect.delimiter
    except csv.Error:
        return ","


def parse_upload(filename: str, file_bytes: bytes) -> ParseResult:
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        return ParseResult(success=False, lines=[], error=upload_size_error())

    lower = filename.lower()
    try:
        if lower.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0)
            lines = df.fillna("").astype(str).to_dict(orient="records")
            return ParseResult(success=True, lines=lines, row_count=len(lines))

        encoding = _detect_encoding(file_bytes)
        text = file_bytes.decode(encoding, errors="replace")
        sep = _detect_separator(text)
        df = pd.read_csv(io.StringIO(text), sep=sep)
        lines = df.fillna("").astype(str).to_dict(orient="records")
        return ParseResult(success=True, lines=lines, encoding=encoding, separator=sep, row_count=len(lines))
    except Exception as exc:
        return ParseResult(success=False, lines=[], error=f"Parse failed: {exc}")
