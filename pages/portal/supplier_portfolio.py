"""Member Supplier Portfolio portal page (placeholder)."""

from __future__ import annotations

from auth.session import get_session
from theme.components import render_page_header
from theme.member_templates import render_member_template


def render(active_page: str = "supplier_portfolio") -> None:
    session = get_session()
    render_page_header(session.display_name)
    # Render static member Supplier Portfolio prototype HTML.
    render_member_template("supplier-portfolio")
