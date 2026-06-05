"""HubSpot login session flags stored in Streamlit session_state."""

from __future__ import annotations

import streamlit as st

AUTH_KEY = "authenticated"
PROFILE_KEY = "hubspot_oauth_profile"
CALLBACK_READY_KEY = "hubspot_callback_ready"
ACCESS_TOKEN_KEY = "hubspot_access_token"


def is_authenticated() -> bool:
    return bool(st.session_state.get(AUTH_KEY))


def show_callback_screen() -> bool:
    return bool(st.session_state.get(CALLBACK_READY_KEY))


def get_profile() -> dict:
    profile = st.session_state.get(PROFILE_KEY)
    return profile if isinstance(profile, dict) else {}


def save_oauth_result(
    *,
    profile: dict,
    access_token: str = "",
) -> None:
    st.session_state[PROFILE_KEY] = profile
    if access_token:
        st.session_state[ACCESS_TOKEN_KEY] = access_token
    st.session_state[CALLBACK_READY_KEY] = True
    st.session_state[AUTH_KEY] = False
    st.session_state.pop("user_session", None)


def complete_login(*, dashboard_page: str = "hub_dashboard") -> None:
    st.session_state[AUTH_KEY] = True
    st.session_state[CALLBACK_READY_KEY] = False
    st.session_state.active_page = dashboard_page
    st.session_state.pop("user_session", None)


def clear_login() -> None:
    for key in (AUTH_KEY, PROFILE_KEY, CALLBACK_READY_KEY, ACCESS_TOKEN_KEY, "hubspot_oauth_state"):
        st.session_state.pop(key, None)
