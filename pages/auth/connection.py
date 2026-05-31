"""SSO Connection screen — entry point for all roles."""

from __future__ import annotations

import html
import os

import streamlit as st

from theme.html_utils import render_html
from theme.tokens import BORDER, CARD_BG, ORANGE, TEXT_MUTED, TEXT_PRIMARY


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


def render() -> None:
    render_html(
        f"""
        <style>
        section[data-testid="stSidebar"] {{ display: none !important; }}
        .block-container {{ max-width: 560px !important; padding-top: 4rem !important; }}
        div[data-testid="stButton"] button[kind="primary"] {{
            width: 100%;
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 2px !important;
            padding: 0.85rem 1rem !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }}
        div[data-testid="stButton"] button[kind="primary"]:hover {{
            background-color: #222222 !important;
        }}
        </style>
        """
    )

    render_html(
        f"""
        <div style="
            background:{CARD_BG};
            border:1px solid {BORDER};
            border-radius:4px;
            padding:3rem 2.5rem 2rem 2.5rem;
            text-align:center;
            margin-bottom:0.5rem;
        ">
            <div style="font-size:2rem;font-weight:800;color:#3D3D3D;line-height:1.1;margin-bottom:0.35rem;">
                <span style="color:{ORANGE};">N!</span>
                <span style="color:#C4C4C4;font-weight:400;margin:0 0.35rem;">|</span>
                NEXUS
            </div>
            <div style="color:{ORANGE};font-size:0.62rem;font-weight:700;letter-spacing:0.14em;
                        text-transform:uppercase;margin-bottom:2.25rem;">
                The Automotive Aftermarket Company
            </div>
            <h1 style="font-size:1.65rem;font-weight:700;color:{TEXT_PRIMARY};margin:0 0 0.5rem 0;">
                Connection
            </h1>
            <p style="color:{TEXT_MUTED};font-size:0.95rem;margin:0 0 1.5rem 0;">
                Access your customer area.
            </p>
        </div>
        """
    )

    if st.button("Sign in with SSO", type="primary", use_container_width=True):
        st.session_state.sso_clicked = True
        st.rerun()

    create_url = html.escape(_create_account_url())
    render_html(
        f"""
        <p style="text-align:center;color:{TEXT_MUTED};font-size:0.88rem;margin-top:1.5rem;">
            Don't have an account ?
            <a href="{create_url}" target="_blank" style="color:{TEXT_PRIMARY};font-weight:700;text-decoration:none;">
                Create an account
            </a>
        </p>
        """
    )


def handle_sso_sign_in() -> bool:
    """Return True when user is authenticated (JWT, prior session, or SSO complete)."""
    if st.session_state.get("authenticated"):
        return True

    if st.query_params.get("jwt"):
        st.session_state.authenticated = True
        return True

    if not st.session_state.get("sso_clicked"):
        return False

    sso_url = _sso_login_url()
    mock_mode = os.environ.get("MOCK_SSO", "true").lower() == "true"

    if mock_mode and "hubspot.com" in sso_url:
        st.session_state.authenticated = True
        st.session_state.pop("sso_clicked", None)
        return True

    st.link_button("Continue to SSO →", sso_url, use_container_width=True)
    return False
