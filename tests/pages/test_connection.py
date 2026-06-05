"""Unit tests for pages.auth.connection."""

from __future__ import annotations
import os
from pages.auth import connection


def test_sso_button_href_mock_mode(monkeypatch) -> None:
    monkeypatch.delenv("HUBSPOT_CLIENT_ID", raising=False)
    monkeypatch.delenv("HUBSPOT_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("HUBSPOT_REDIRECT_URI", raising=False)
    monkeypatch.setenv("MOCK_SSO", "true")
    monkeypatch.setenv("SSO_LOGIN_URL", "https://app.hubspot.com/login")
    assert connection._sso_button_href() == "?sso=1"


def test_sso_button_href_oauth_overrides_mock(monkeypatch, streamlit_session) -> None:
    monkeypatch.setenv("MOCK_SSO", "true")
    monkeypatch.setenv("HUBSPOT_CLIENT_ID", "cid")
    monkeypatch.setenv("HUBSPOT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("HUBSPOT_REDIRECT_URI", "http://localhost:8505/auth/hubspot/callback")
    href = connection._sso_button_href()
    assert "app.hubspot.com/oauth/authorize" in href
    assert href != "?sso=1"


def test_sso_button_href_live_mode(monkeypatch) -> None:
    monkeypatch.setenv("MOCK_SSO", "false")
    monkeypatch.setenv("SSO_LOGIN_URL", "https://idp.example.com/sso")
    assert connection._sso_button_href() == "https://idp.example.com/sso"


def test_sso_button_href_hubspot_oauth(monkeypatch, streamlit_session) -> None:
    monkeypatch.setenv("MOCK_SSO", "false")
    monkeypatch.setenv("HUBSPOT_CLIENT_ID", "cid")
    monkeypatch.setenv("HUBSPOT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("HUBSPOT_REDIRECT_URI", "http://localhost:8505/auth/hubspot/callback")
    href = connection._sso_button_href()
    assert "app.hubspot.com/oauth/authorize" in href
    assert "client_id=cid" in href
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8504%2Fauth%2Fhubspot%2Fcallback" in href


def test_logo_data_uri_when_file_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(connection, "image_path", lambda name: tmp_path / name)
    assert connection._logo_data_uri() is None


def test_handle_sso_sign_in_mock_flow(streamlit_session, monkeypatch) -> None:
    monkeypatch.delenv("HUBSPOT_CLIENT_ID", raising=False)
    monkeypatch.delenv("HUBSPOT_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("HUBSPOT_REDIRECT_URI", raising=False)
    monkeypatch.setenv("MOCK_SSO", "true")
    monkeypatch.setenv("SSO_LOGIN_URL", "https://app.hubspot.com/login")
    streamlit_session.sso_clicked = True

    assert connection.handle_sso_sign_in() is True
    assert streamlit_session.authenticated is True


def test_try_process_oauth_callback_success(streamlit_session, monkeypatch) -> None:
    import importlib
    import streamlit as st

    conn = importlib.import_module("pages.auth.connection")
    query_params = {"code": "test-code", "state": "state-1"}
    monkeypatch.setattr(st, "query_params", query_params, raising=False)
    streamlit_session.pop("hubspot_callback_ready", None)
    streamlit_session.pop("hubspot_oauth_error", None)

    monkeypatch.setenv("HUBSPOT_CLIENT_ID", "cid")
    monkeypatch.setenv("HUBSPOT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("HUBSPOT_REDIRECT_URI", "http://localhost:8505/auth/hubspot/callback")
    monkeypatch.delenv("HUBSPOT_COMPANY_ID", raising=False)
    monkeypatch.setattr(conn, "oauth_enabled", lambda: True)
    monkeypatch.setattr(
        conn,
        "process_oauth_callback",
        lambda code, state: {
            "profile": {"user": "user@example.com", "hub_id": 1, "app_id": 2},
            "access_token": "token",
        },
    )
    monkeypatch.setattr(conn, "mint_jwt_from_hubspot", lambda *_: None)
    monkeypatch.setattr(conn, "_clear_oauth_query_params", lambda: query_params.clear())

    assert conn.try_process_oauth_callback() is True
    assert streamlit_session.get("hubspot_callback_ready") is True
    assert streamlit_session.hubspot_oauth_profile["user"] == "user@example.com"


def test_handle_sso_query_ignored_when_oauth_enabled(streamlit_session, monkeypatch) -> None:
    monkeypatch.setenv("HUBSPOT_CLIENT_ID", "cid")
    monkeypatch.setenv("HUBSPOT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("HUBSPOT_REDIRECT_URI", "http://localhost:8505/auth/hubspot/callback")
    streamlit_session.sso_clicked = True

    assert connection.handle_sso_sign_in() is False
    assert not streamlit_session.get("authenticated")


def test_handle_sso_sign_in_requires_click(streamlit_session, monkeypatch) -> None:
    monkeypatch.delenv("MOCK_SSO", raising=False)
    streamlit_session.pop("authenticated", None)
    streamlit_session.pop("sso_clicked", None)
    assert connection.handle_sso_sign_in() is False
