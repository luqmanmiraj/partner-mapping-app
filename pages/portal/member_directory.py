"""Member Directory page — REF.MEMBER_ITG with fixture fallback."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from auth.snowflake_session import scoped_connection
from data.member_directory_fixtures import DEMO_COMPANIES
from data.portal_loaders import load_member_directory
from theme.components import render_page_header
from widgets.decision_makers_list import render_decision_makers_list
from widgets.identify_partners_filter import render_identify_partners_filter
from widgets.member_directory_map import render_member_directory_map


def render(active_page: str = "member_directory") -> None:
    session = get_session()
    render_page_header(session.display_name)

    render_identify_partners_filter()

    companies = DEMO_COMPANIES
    use_sf = st.session_state.get("use_snowflake", False)
    passcode = st.session_state.get("passcode", "")
    with scoped_connection(passcode, force_demo=not use_sf) as conn:
        if conn is not None:
            loaded = load_member_directory(conn)
            if loaded:
                companies = [
                    {
                        "name": c["name"],
                        "country": c["country"],
                        "role": c.get("level", "Member"),
                    }
                    for c in loaded
                ]

    left_col, right_col = st.columns(2, gap="large")
    with left_col:
        render_decision_makers_list(companies)
    with right_col:
        render_member_directory_map()
