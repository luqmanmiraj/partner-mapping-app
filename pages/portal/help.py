"""Help & Support Center Portal Page Coordinator."""

from __future__ import annotations

from auth.session import get_session
from theme.components import render_page_header
from widgets.help import render_help_center


def render(active_page: str = "help") -> None:
    """Render the Help & Support Center page."""
    session = get_session()
    render_page_header(session.display_name)
    render_help_center()
