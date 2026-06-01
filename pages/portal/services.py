"""Services Portal Page Coordinator — routes to Catalog or Single Service views."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from theme.components import render_page_header
from widgets.services import render_services_catalog
from widgets.services_single import render_service_single


def render(active_page: str = "services") -> None:
    """Render the active sub-section for Services."""
    session = get_session()
    render_page_header(session.display_name)

    # Check if a specific service detail view is requested
    active_service_id = st.session_state.get("active_service_id")

    if active_service_id:
        render_service_single(active_service_id)
    else:
        render_services_catalog()
