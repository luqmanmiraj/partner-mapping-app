"""News & Insights Portal Page Coordinator."""

from __future__ import annotations

from auth.session import get_session
from theme.components import render_page_header
from widgets.news import render_news_insights


def render(active_page: str = "news") -> None:
    """Render the News & Insights page."""
    session = get_session()
    render_page_header(session.display_name)
    render_news_insights()
