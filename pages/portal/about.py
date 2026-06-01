"""About portal page — company profile sections from .prototype/company/."""

from __future__ import annotations

from auth.session import get_session
from data.about_page_fixtures import (
    BRAND_FILES,
    COVER_PROFILE,
    INTRO_PARAGRAPHS,
    PILLARS,
    PILLARS_FEATURE,
)
from theme.components import render_page_header
from widgets.about_about import render_about_about
from widgets.about_brands import render_about_brands
from widgets.about_cover import render_about_cover
from widgets.about_pillars import render_about_pillars


def render(active_page: str = "about") -> None:
    session = get_session()
    render_page_header(session.display_name)

    render_about_cover(COVER_PROFILE)
    render_about_about(INTRO_PARAGRAPHS)
    render_about_pillars(PILLARS, PILLARS_FEATURE)
    render_about_brands(BRAND_FILES)
