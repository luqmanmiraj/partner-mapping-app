"""Unit tests for services.file_parser."""

from __future__ import annotations

from constants import MAX_UPLOAD_BYTES
from services.file_parser import parse_upload


def test_parse_csv_utf8_comma(sample_csv_bytes: bytes) -> None:
    result = parse_upload("declaration.csv", sample_csv_bytes)
    assert result.success is True
    assert result.row_count == 2
    assert result.encoding == "utf-8"
    assert result.separator == ","
    assert float(result.lines[0]["amount"]) == 1250.5


def test_parse_csv_semicolon_delimiter() -> None:
    raw = "amount;partner\n100;ACME\n".encode("utf-8")
    result = parse_upload("legacy.csv", raw)
    assert result.success is True
    assert result.row_count == 1
    assert result.separator == ";"


def test_parse_empty_file_returns_no_lines() -> None:
    result = parse_upload("empty.csv", b"amount,partner\n")
    assert result.success is True
    assert result.row_count == 0
    assert result.lines == []


def test_parse_rejects_oversized_file() -> None:
    huge = b"x" * (MAX_UPLOAD_BYTES + 1)
    result = parse_upload("big.csv", huge)
    assert result.success is False
    assert "250" in result.error


def test_parse_invalid_excel_returns_error() -> None:
    result = parse_upload("broken.xlsx", b"not-a-real-xlsx")
    assert result.success is False
    assert result.error.startswith("Parse failed:")
