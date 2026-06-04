"""Unit tests for widgets.company_tabs."""

from __future__ import annotations

from widgets.company_tabs import (
    TAB_ABOUT,
    TAB_CONTACTS,
    TAB_NEWS,
    _TABS,
    company_tabs_styles,
)


def test_tab_constants() -> None:
    ids = {tab_id for tab_id, _, _ in _TABS}
    assert ids == {TAB_ABOUT, TAB_CONTACTS, TAB_NEWS}


def test_company_tabs_styles_targets_nav_key() -> None:
    css = company_tabs_styles()
    assert "company_tabs_nav" in css
    assert "border-bottom" in css


def test_active_tab_defaults_to_about(streamlit_session) -> None:
    from widgets.company_tabs import _active_tab

    assert _active_tab() == TAB_ABOUT


def test_active_tab_invalid_session_value_falls_back(streamlit_session) -> None:
    from widgets.company_tabs import _SESSION_KEY, _active_tab

    streamlit_session[_SESSION_KEY] = "invalid"
    assert _active_tab() == TAB_ABOUT
