"""Member Offers portal page (placeholder)."""

from __future__ import annotations

from auth.session import get_session
from theme.components import render_page_header
from theme.member_templates import render_member_template


def render(active_page: str = "offers") -> None:
    session = get_session()
    render_page_header(session.display_name, subtitle="Negotiated offers for your network")
    # Render static member Offers prototype HTML so the page matches the design.
    render_member_template("offers")
