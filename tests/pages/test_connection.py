"""Unit tests for pages.auth.connection."""

from __future__ import annotations

import os

from pages.auth import connection


def test_sso_button_href_mock_mode(monkeypatch) -> None:
    monkeypatch.setenv("MOCK_SSO", "true")
    monkeypatch.setenv("SSO_LOGIN_URL", "https://app.hubspot.com/login")
    assert connection._sso_button_href() == "?sso=1"


def test_sso_button_href_live_mode(monkeypatch) -> None:
    monkeypatch.setenv("MOCK_SSO", "false")
    monkeypatch.setenv("SSO_LOGIN_URL", "https://idp.example.com/sso")
    assert connection._sso_button_href() == "https://idp.example.com/sso"


def test_logo_data_uri_when_file_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(connection, "image_path", lambda name: tmp_path / name)
    assert connection._logo_data_uri() is None


def test_handle_sso_sign_in_mock_flow(streamlit_session, monkeypatch) -> None:
    monkeypatch.setenv("MOCK_SSO", "true")
    monkeypatch.setenv("SSO_LOGIN_URL", "https://app.hubspot.com/login")
    streamlit_session.sso_clicked = True

    assert connection.handle_sso_sign_in() is True
    assert streamlit_session.authenticated is True


def test_handle_sso_sign_in_requires_click(streamlit_session, monkeypatch) -> None:
    monkeypatch.delenv("MOCK_SSO", raising=False)
    streamlit_session.pop("authenticated", None)
    streamlit_session.pop("sso_clicked", None)
    assert connection.handle_sso_sign_in() is False
