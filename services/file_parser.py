"""BRD Step 1 — file parsing (encoding, separator, lines, Excel sheet/header detection)."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass

import pandas as pd

from constants import MAX_PARSE_ROWS, MAX_UPLOAD_BYTES, upload_size_error

_UNNAMED_RE = re.compile(r"^unnamed", re.IGNORECASE)


@dataclass
class ParseResult:
    success: bool
    lines: list[dict]
    encoding: str = "utf-8"
    separator: str = ","
    error: str = ""
    row_count: int = 0
    sheet_name: str = ""
    header_row: int = 0
    truncated: bool = False
    warnings: list[str] | None = None


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


def _clean_header(value: object, index: int) -> str:
    text = str(value).strip() if value is not None and str(value) != "nan" else ""
    if not text or _UNNAMED_RE.match(text):
        return f"column_{index + 1}"
    return text


def _find_header_row(preview: pd.DataFrame, max_scan: int = 40) -> int:
    best_row = 0
    best_score = 0
    limit = min(max_scan, len(preview))
    for i in range(limit):
        row = preview.iloc[i]
        non_empty = 0
        for val in row:
            if val is not None and str(val).strip() not in ("", "nan"):
                non_empty += 1
        if non_empty > best_score:
            best_score = non_empty
            best_row = i
    return best_row if best_score >= 2 else 0


def _sheet_name_bonus(name: str) -> int:
    low = name.lower()
    bonus = 0
    for token, pts in (
        ("turnover", 40),
        ("sales", 35),
        ("report", 30),
        ("hierarchy", 25),
        ("consolidation", 25),
        ("reporting", 25),
        (" by ", 20),
        ("nai", 15),
        ("nexus", 15),
        ("data", 10),
    ):
        if token in low:
            bonus += pts
    if low.startswith("z_") or "standard" in low or low.startswith("sheet"):
        bonus -= 40
    return bonus


def _score_sheet_preview(preview: pd.DataFrame, sheet_name: str) -> int:
    if preview.empty:
        return 0
    header_idx = _find_header_row(preview)
    body = preview.iloc[header_idx + 1 :].dropna(how="all")
    raw_cols = int(preview.iloc[header_idx].notna().sum())
    # Pivot/meta sheets can have dozens of sparse columns — cap for fair comparison.
    cols = min(raw_cols, 12)
    rows = min(int(body.shape[0]), 80)
    return rows * max(cols, 1) + _sheet_name_bonus(sheet_name)


def _dataframe_from_sheet(raw: io.BytesIO, sheet_name: str) -> pd.DataFrame:
    preview = pd.read_excel(raw, sheet_name=sheet_name, header=None, nrows=60)
    raw.seek(0)
    header_idx = _find_header_row(preview)
    df = pd.read_excel(raw, sheet_name=sheet_name, header=header_idx)
    df = df.dropna(how="all")
    df.columns = [_clean_header(c, i) for i, c in enumerate(df.columns)]
    # Drop columns that are entirely empty
    keep = [c for c in df.columns if not df[c].astype(str).str.strip().eq("").all()]
    if keep:
        df = df[keep]
    return df


def _candidate_sheet_names(names: list[str]) -> list[str]:
    """Prefer turnover/report sheets over pivot metadata tabs."""
    by_sheets = [n for n in names if n.lower().startswith("by ")]
    if by_sheets:
        return by_sheets
    reportish = [
        n
        for n in names
        if any(
            token in n.lower()
            for token in ("turnover", "sales", "report", "consolidation", "nai", "data")
        )
    ]
    if reportish:
        return reportish
    return names


def _pick_excel_sheet(file_bytes: bytes) -> tuple[pd.DataFrame, str]:
    bio = io.BytesIO(file_bytes)
    workbook = pd.ExcelFile(bio)
    if not workbook.sheet_names:
        return pd.DataFrame(), ""

    candidates = _candidate_sheet_names(workbook.sheet_names)
    best_name = candidates[0]
    best_score = -1
    for name in candidates:
        bio.seek(0)
        try:
            preview = pd.read_excel(bio, sheet_name=name, header=None, nrows=60)
        except Exception:
            continue
        score = _score_sheet_preview(preview, name)
        if score > best_score:
            best_score = score
            best_name = name

    bio.seek(0)
    df = _dataframe_from_sheet(bio, best_name)
    return df, best_name


def _lines_from_dataframe(df: pd.DataFrame) -> tuple[list[dict], list[str]]:
    warnings: list[str] = []
    if df.empty:
        return [], ["No data rows found after header detection."]

    lines = df.fillna("").astype(str).to_dict(orient="records")
    # Drop rows that are completely empty strings
    cleaned: list[dict] = []
    for row in lines:
        if any(str(v).strip() for v in row.values()):
            cleaned.append(row)

    truncated = False
    total = len(cleaned)
    if total > MAX_PARSE_ROWS:
        truncated = True
        warnings.append(
            f"File has {total:,} rows; processing first {MAX_PARSE_ROWS:,} for performance."
        )
        cleaned = cleaned[:MAX_PARSE_ROWS]

    unnamed = [c for c in df.columns if _UNNAMED_RE.match(str(c)) or str(c).startswith("column_")]
    if unnamed:
        warnings.append(
            f"{len(unnamed)} column(s) had no header in the file and were auto-named."
        )

    return cleaned, warnings


def parse_upload(filename: str, file_bytes: bytes) -> ParseResult:
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        return ParseResult(success=False, lines=[], error=upload_size_error())

    lower = filename.lower()
    warnings: list[str] = []
    try:
        if lower.endswith((".xlsx", ".xls")):
            df, sheet_name = _pick_excel_sheet(file_bytes)
            if df.empty:
                return ParseResult(
                    success=False,
                    lines=[],
                    error="No tabular data found in workbook. Check sheet layout and headers.",
                )
            lines, sheet_warnings = _lines_from_dataframe(df)
            warnings.extend(sheet_warnings)
            if not lines:
                return ParseResult(
                    success=False,
                    lines=[],
                    error="No data rows found in Excel file.",
                    sheet_name=sheet_name,
                    warnings=warnings,
                )
            truncated = len(warnings) > 0 and any("processing first" in w for w in warnings)
            return ParseResult(
                success=True,
                lines=lines,
                row_count=len(lines),
                sheet_name=sheet_name,
                truncated=truncated,
                warnings=warnings or None,
            )

        encoding = _detect_encoding(file_bytes)
        text = file_bytes.decode(encoding, errors="replace")
        sep = _detect_separator(text)
        df = pd.read_csv(io.StringIO(text), sep=sep)
        df.columns = [_clean_header(c, i) for i, c in enumerate(df.columns)]
        lines, csv_warnings = _lines_from_dataframe(df)
        warnings.extend(csv_warnings)
        if not lines:
            return ParseResult(success=False, lines=[], error="No data rows found in CSV file.")
        truncated = any("processing first" in w for w in warnings)
        return ParseResult(
            success=True,
            lines=lines,
            encoding=encoding,
            separator=sep,
            row_count=len(lines),
            truncated=truncated,
            warnings=warnings or None,
        )
    except Exception as exc:
        return ParseResult(success=False, lines=[], error=f"Parse failed: {exc}")
