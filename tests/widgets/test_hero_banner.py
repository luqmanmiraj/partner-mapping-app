"""Unit tests for widgets.hero_banner HTML/CSS builders."""

from __future__ import annotations

from content_policies.hub_dashboard import HubDashboardPolicy
from widgets.hero_banner import _PREFIX, hero_banner_styles


def test_hero_banner_styles_include_prefix() -> None:
    css = hero_banner_styles()
    assert f".{_PREFIX}__banner" in css
    assert "flex" in css


def test_render_hero_banner_builds_markup(monkeypatch) -> None:
    captured: list[str] = []

    def fake_render_st_html_page(css: str, html: str, *, width: str = "stretch") -> None:
        captured.append(css)
        captured.append(html)

    monkeypatch.setattr("widgets.hero_banner.render_st_html_page", fake_render_st_html_page)

    from widgets.hero_banner import render_hero_banner

    policy = HubDashboardPolicy(role_key="supplier", declarant_type="supplier")
    render_hero_banner(policy)

    assert len(captured) == 2
    assert policy.hero_headline in captured[1]
    for bullet in policy.hero_bullets:
        assert bullet in captured[1]
