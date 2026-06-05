"""SSO Connection screen — entry point for all roles."""

from __future__ import annotations

import base64
import html
import mimetypes
import os

import streamlit as st

from auth.hubspot_bridge import apply_jwt_to_session, mint_jwt_from_hubspot
from services.hubspot_oauth_service import (
    build_authorize_url,
    new_state,
    oauth_enabled,
    persist_oauth_state,
    process_oauth_callback,
)
from services.hubspot_session import (
    complete_login,
    get_profile,
    is_authenticated,
    save_oauth_result,
    show_callback_screen,
)
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


def _ensure_oauth_state() -> str:
    state = st.session_state.get("hubspot_oauth_state")
    if not state:
        state = new_state()
        st.session_state.hubspot_oauth_state = state
        persist_oauth_state(state)
    return state


def _sso_button_href() -> str:
    """Link target for SSO control (HubSpot OAuth when configured, else mock/fallback)."""
    if oauth_enabled():
        return build_authorize_url(state=_ensure_oauth_state())

    mock_mode = os.environ.get("MOCK_SSO", "true").lower() == "true"
    sso_url = _sso_login_url()
    if mock_mode and "hubspot.com" in sso_url:
        return "?sso=1"
    return sso_url


def _sso_link_opens_new_window(href: str) -> bool:
    """External OAuth/SSO URLs must break out of st.html iframe."""
    return href.startswith("http://") or href.startswith("https://")


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

    link_target = (
        ' target="_top" rel="noopener noreferrer"'
        if _sso_link_opens_new_window(sso_href)
        else ""
    )

    render_html(
        f"""
        <div class="{p}">
            <div class="{p}__card">
                {logo_block}
                <h1 class="{p}__title">Connection</h1>
                <p class="{p}__subtitle">Access your customer area.</p>
                <a class="{p}__btn-sso" href="{sso_url}"{link_target}>Sign in with SSO</a>
                <p class="{p}__footer">
                    Don't have an account ?
                    <a class="{p}__footer-link" href="{create_url}"
                       target="_blank" rel="noopener noreferrer">Create an account</a>
                </p>
            </div>
        </div>
        """
    )


def _inject_callback_button_styles() -> None:
    inject_parent_styles(
        """
        [data-testid="stMain"] .st-key-hubspot_continue_row div[data-testid="stButton"] > button {
            display: inline-block !important;
            width: auto !important;
            min-width: 180px !important;
            padding: 0.55rem 1.5rem !important;
            border-radius: 5px !important;
            background: #000000 !important;
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 1px solid #000000 !important;
            font-weight: 600 !important;
        }
        [data-testid="stMain"] .st-key-hubspot_continue_row div[data-testid="stButton"] > button:hover {
            background: #1a1a1a !important;
            background-color: #1a1a1a !important;
            border-color: #1a1a1a !important;
        }
        [data-testid="stMain"] .st-key-hubspot_continue_row {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-top: 0.5rem !important;
        }
        """,
        style_id="nexus-hubspot-callback-continue",
    )


def _clear_oauth_query_params() -> None:
    for key in ("code", "state"):
        try:
            del st.query_params[key]
        except Exception:
            pass


def try_process_oauth_callback() -> bool:
    """
    Process HubSpot OAuth callback query params (?code=&state=).

    Returns True when the callback confirmation screen should be shown.
    """
    if show_callback_screen():
        return True

    code = st.query_params.get("code")
    if not code or not oauth_enabled():
        return False

    state = st.query_params.get("state")
    try:
        result = process_oauth_callback(str(code), str(state) if state else None)
        profile = result["profile"]
        access_token = result.get("access_token", "")

        company_id = os.environ.get("HUBSPOT_COMPANY_ID", "")
        if company_id:
            minted = mint_jwt_from_hubspot(company_id)
            if minted and minted.get("token"):
                apply_jwt_to_session(minted["token"])

        save_oauth_result(profile=profile, access_token=access_token)
        _clear_oauth_query_params()
        st.session_state.pop("hubspot_oauth_error", None)
        return True
    except Exception as exc:
        st.session_state.hubspot_oauth_error = str(exc)
        _clear_oauth_query_params()
        return False


def render() -> None:
    _inject_login_styles()

    oauth_error = st.session_state.get("hubspot_oauth_error")
    if oauth_error:
        st.error(f"HubSpot login failed: {oauth_error}")

    if show_callback_screen():
        _render_hubspot_callback_result()
        return

    _render_login_card(sso_href=_sso_button_href())


def _render_hubspot_callback_result() -> None:
    profile = get_profile()
    email = html.escape(str(profile.get("user", "unknown")))
    hub_id = html.escape(str(profile.get("hub_id", "")))
    app_id = html.escape(str(profile.get("app_id", "")))
    hub_domain = html.escape(str(profile.get("hub_domain", "")))
    company_id = html.escape(str(profile.get("company_id", "")) or "—")

    render_html(
        f"""
        <div class="{_PREFIX}">
            <div class="{_PREFIX}__card" style="margin-top: 120px;">
                <h1 class="{_PREFIX}__title">Signed in with HubSpot</h1>
                <p class="{_PREFIX}__subtitle" style="margin-bottom: 20px;">
                    Your account is connected. Review the details below, then continue.
                </p>
                <div style="text-align:left;max-width:440px;margin:0 auto 24px auto;color:#333;">
                    <p><strong>User:</strong> {email}</p>
                    <p><strong>Hub ID:</strong> {hub_id}</p>
                    <p><strong>Hub domain:</strong> {hub_domain}</p>
                    <p><strong>App ID:</strong> {app_id}</p>
                    <p><strong>Company ID:</strong> {company_id}</p>
                </div>
            </div>
        </div>
        """
    )

    _inject_callback_button_styles()
    with st.container(key="hubspot_continue_row"):
        if st.button("Continue", type="primary", key="hubspot_continue"):
            complete_login(dashboard_page="hub_dashboard")
            st.rerun()


def handle_sso_sign_in() -> bool:
    """Return True when user is authenticated (JWT, prior session, or SSO complete)."""
    if is_authenticated():
        return True

    if st.query_params.get("jwt"):
        st.session_state.authenticated = True
        return True

    if show_callback_screen():
        return False

    if st.query_params.get("sso"):
        if oauth_enabled():
            try:
                del st.query_params["sso"]
            except Exception:
                pass
            return False
        st.session_state.sso_clicked = True
        try:
            del st.query_params["sso"]
        except Exception:
            pass

    if not st.session_state.get("sso_clicked"):
        return False

    sso_url = _sso_login_url()
    mock_mode = os.environ.get("MOCK_SSO", "true").lower() == "true"

    if mock_mode and "hubspot.com" in sso_url and not oauth_enabled():
        st.session_state.authenticated = True
        st.session_state.pop("sso_clicked", None)
        return True

    return False
