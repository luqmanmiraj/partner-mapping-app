"""SSO Connection screen — entry point for all roles."""

from __future__ import annotations

import base64
import html
import mimetypes
import os

import streamlit as st

from theme.html_utils import inject_parent_styles, render_html
from theme.paths import image_path

LOGO_FILE = "logo.jpg"
_PREFIX = "nexus-login"


def _sso_login_url() -> str:
    return os.environ.get(
        "SSO_LOGIN_URL",
        os.environ.get("HUBSPOT_SSO_URL", "https://app.hubspot.com/login"),
    )


def _create_account_url() -> str:
    return os.environ.get(
        "CREATE_ACCOUNT_URL",
        "https://www.nexusautomotiveinternational.eu/",
    )


def _logo_data_uri() -> str | None:
    path = image_path(LOGO_FILE)
    if not path.is_file():
        return None
    mime = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _sso_button_href() -> str:
    """Link target for the SSO control (mock uses query param; live uses IdP URL)."""
    mock_mode = os.environ.get("MOCK_SSO", "true").lower() == "true"
    sso_url = _sso_login_url()
    if mock_mode and "hubspot.com" in sso_url:
        return "?sso=1"
    return sso_url


def _login_shell_css() -> str:
    """Streamlit chrome only — not part of the login component design."""
    return """
        section[data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] {
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
        }
        .stApp { background-color: #ededed !important; }
        [data-testid="stMain"] [data-testid="stMainBlockContainer"],
        [data-testid="stMain"] [data-testid="block-container"],
        section.main > div,
        section.main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            margin-top: 0 !important;
        }
        [data-testid="stMain"] [data-testid="stMainBlockContainer"] > div {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 100vh !important;
            width: 100% !important;
            padding: 0 1rem !important;
            box-sizing: border-box !important;
            gap: 0 !important;
        }
        [data-testid="stMain"] [data-testid="block-container"] {
            max-width: 720px !important;
            width: 100% !important;
            margin: 0 auto !important;
        }
        [data-testid="stMain"] [data-testid="stElementContainer"]:has(iframe[height="0"]) {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
    """


def _login_component_css() -> str:
    """Prefixed selectors from .prototype/login.html — scoped to .nexus-login."""
    p = _PREFIX
    return f"""
        .{p} {{
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                Helvetica, Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
        }}

        .{p} *,
        .{p} *::before,
        .{p} *::after {{
            box-sizing: border-box;
        }}

        .{p}__card {{
            background-color: #ffffff;
            width: 100%;
            max-width: 630px;
            padding: 60px 40px;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: 1px solid #e0e0e0;
            text-align: center;
            margin-top: 200px;
        }}

        .{p}__logo-wrap {{
            margin-bottom: 40px;
        }}

        .{p}__logo {{
            max-width: 240px;
            width: 100%;
            height: auto;
            display: inline-block;
        }}

        .{p}__title {{
            color: #111111;
            font-size: 32px;
            font-weight: 700;
            margin: 0 0 12px 0;
            letter-spacing: -0.5px;
            line-height: 1.2;
        }}

        .{p}__subtitle {{
            color: #777777;
            font-size: 18px;
            margin: 0 0 40px 0;
            font-weight: 400;
            line-height: 1.4;
        }}

        .{p}__btn-sso {{
            display: block;
            width: 100%;
            max-width: 440px;
            margin: 0 auto 40px auto;
            background-color: #141414;
            color: #ffffff !important;
            font-size: 16px;
            font-weight: 500;
            padding: 16px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            text-align: center;
            transition: background-color 0.2s ease;
            line-height: 1.25;
        }}

        .{p}__btn-sso:hover {{
            background-color: #262626;
            color: #ffffff !important;
        }}

        .{p}__footer {{
            color: #888888;
            font-size: 16px;
            font-weight: 400;
            margin: 0;
            line-height: 1.5;
        }}

        .{p}__footer-link {{
            color: #777777;
            text-decoration: none;
            font-weight: 700;
        }}

        .{p}__footer-link:hover {{
            text-decoration: underline;
        }}

    """


def _inject_login_styles() -> None:
    inject_parent_styles(
        _login_shell_css() + _login_component_css(),
        style_id="nexus-login-shell",
    )


def _render_login_card(*, sso_href: str) -> None:
    p = _PREFIX
    logo_uri = _logo_data_uri()
    create_url = html.escape(_create_account_url())
    sso_url = html.escape(sso_href, quote=True)

    if logo_uri:
        logo_block = (
            f'<div class="{p}__logo-wrap">'
            f'<img class="{p}__logo" src="{logo_uri}" '
            f'alt="NEXUS — The Automotive Aftermarket Company" />'
            f"</div>"
        )
    else:
        logo_block = f'<p class="{p}__title" style="margin-bottom:40px;">NEXUS</p>'

    render_html(
        f"""
        <div class="{p}">
            <div class="{p}__card">
                {logo_block}
                <h1 class="{p}__title">Connection</h1>
                <p class="{p}__subtitle">Access your customer area.</p>
                <a class="{p}__btn-sso" href="{sso_url}">Sign in with SSO</a>
                <p class="{p}__footer">
                    Don't have an account ?
                    <a class="{p}__footer-link" href="{create_url}"
                       target="_blank" rel="noopener noreferrer">Create an account</a>
                </p>
            </div>
        </div>
        """
    )


def render() -> None:
    _inject_login_styles()
    _render_login_card(sso_href=_sso_button_href())


def handle_sso_sign_in() -> bool:
    """Return True when user is authenticated (JWT, prior session, or SSO complete)."""
    if st.session_state.get("authenticated"):
        return True

    if st.query_params.get("jwt"):
        st.session_state.authenticated = True
        return True

    if st.query_params.get("sso"):
        st.session_state.sso_clicked = True
        try:
            del st.query_params["sso"]
        except Exception:
            pass

    if not st.session_state.get("sso_clicked"):
        return False

    sso_url = _sso_login_url()
    mock_mode = os.environ.get("MOCK_SSO", "true").lower() == "true"

    if mock_mode and "hubspot.com" in sso_url:
        st.session_state.authenticated = True
        st.session_state.pop("sso_clicked", None)
        return True

    return False
