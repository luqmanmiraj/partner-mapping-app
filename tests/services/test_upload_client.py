"""Unit tests for services.upload_client."""

from __future__ import annotations

from services.upload_client import UploadResult, upload_declaration


def test_upload_declaration_success(brd_state, sample_csv_bytes: bytes, monkeypatch) -> None:
    monkeypatch.delenv("UPLOAD_API_URL", raising=False)
    result = upload_declaration(
        file_bytes=sample_csv_bytes,
        filename="upload.csv",
        period="Q1-2026",
        currency="EUR",
        comment="test",
        partner_key="MEYLE",
    )
    assert isinstance(result, UploadResult)
    assert result.success is True
    assert result.upload_id.startswith("DEP-")
    assert result.message


def test_upload_declaration_api_url_not_wired(monkeypatch, sample_csv_bytes: bytes) -> None:
    monkeypatch.setenv("UPLOAD_API_URL", "https://api.example/upload")
    result = upload_declaration(
        file_bytes=sample_csv_bytes,
        filename="upload.csv",
        period="Q1-2026",
        currency="EUR",
        comment="",
        partner_key="MEYLE",
    )
    assert result.success is False
    assert "not yet connected" in result.error
