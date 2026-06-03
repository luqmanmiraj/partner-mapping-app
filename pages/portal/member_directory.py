"""Member Directory page — partner search, company list, and map."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from data.member_directory_fixtures import DEMO_COMPANIES
from theme.components import render_page_header
from widgets.decision_makers_list import render_decision_makers_list
from widgets.identify_partners_filter import render_identify_partners_filter
from widgets.member_directory_map import render_member_directory_map


def render(active_page: str = "member_directory") -> None:
    session = get_session()
    render_page_header(session.display_name)

    render_identify_partners_filter()

    left_col, right_col = st.columns(2, gap="large")
    with left_col:
        render_decision_makers_list(DEMO_COMPANIES)
    with right_col:
        render_member_directory_map()
