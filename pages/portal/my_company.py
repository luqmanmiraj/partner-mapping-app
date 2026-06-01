"""My Company portal page — overview and tabbed company profile sections."""

from __future__ import annotations

from auth.session import get_session
from data.my_company_fixtures import (
    ABOUT_TAB,
    CONTACTS,
    DOCUMENTS,
    GALLERY_ITEMS,
    MEDIA_ITEMS,
    NEWS_FEATURED,
    NEWS_SIDEBAR,
    OVERVIEW,
)
from theme.components import render_page_header
from widgets.company_layout import inject_all_company_page_styles
from widgets.company_overview import render_company_overview
from widgets.company_tabs import render_company_tabs


def render(active_page: str = "my_company") -> None:
    session = get_session()
    render_page_header(session.display_name)
    inject_all_company_page_styles()

    render_company_overview(OVERVIEW)

    news_data = {
        "featured": NEWS_FEATURED,
        "sidebar": NEWS_SIDEBAR,
        "documents": DOCUMENTS,
        "videos": MEDIA_ITEMS,
        "gallery": GALLERY_ITEMS,
    }
    render_company_tabs(ABOUT_TAB, CONTACTS, news_data)
