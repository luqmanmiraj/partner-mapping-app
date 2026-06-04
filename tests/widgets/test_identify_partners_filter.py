"""Unit tests for widgets.identify_partners_filter."""

from __future__ import annotations

from widgets.identify_partners_filter import (
    _PREFIX,
    build_identify_partners_html,
    identify_partners_styles,
)


def test_identify_partners_styles_scope() -> None:
    css = identify_partners_styles()
    assert f".{_PREFIX}__title" in css
    assert f".{_PREFIX}__search-input" in css


def test_build_identify_partners_html_structure() -> None:
    html = build_identify_partners_html()
    assert f'class="{_PREFIX}"' in html
    assert "Identify your partners" in html
    assert 'placeholder="Search for a member"' in html
    assert "Filter by Region" in html
