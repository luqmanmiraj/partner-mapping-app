"""Unit tests for widgets.upcoming_features."""

from __future__ import annotations

from content_policies.hub_dashboard import HubDashboardPolicy
from widgets.upcoming_features import _PREFIX, upcoming_features_styles


def test_upcoming_features_styles() -> None:
    css = upcoming_features_styles()
    assert f".{_PREFIX}__banner" in css


def test_render_upcoming_features_includes_blurb(monkeypatch) -> None:
    captured: list[str] = []

    def fake_render(css: str, html: str, *, width: str = "stretch") -> None:
        captured.extend([css, html])

    monkeypatch.setattr("widgets.upcoming_features.render_st_html_page", fake_render)

    from widgets.upcoming_features import render_upcoming_features

    policy = HubDashboardPolicy(
        role_key="member",
        declarant_type="member",
        upcoming_blurb="Soon you will be able to explore supplier performance.",
    )
    render_upcoming_features(policy)
    assert "Soon you will be able to explore supplier performance." in captured[1]
    assert "Upcoming features" in captured[1]
