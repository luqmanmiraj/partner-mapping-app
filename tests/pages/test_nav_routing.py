"""Unit tests for page routing helpers (theme.sidenav, used by portal pages)."""

from __future__ import annotations

from types import SimpleNamespace

from theme.sidenav import (
    hub_portal_nav_for_session,
    remap_active_page_for_declarant,
)


def test_hub_portal_nav_member() -> None:
    session = SimpleNamespace(declarant_type="member")
    labels = [label for label, _, _ in hub_portal_nav_for_session(session)]
    assert "Offers" in labels
    assert "Member Directory" not in labels


def test_hub_portal_nav_supplier() -> None:
    session = SimpleNamespace(declarant_type="supplier")
    labels = [label for label, _, _ in hub_portal_nav_for_session(session)]
    assert "Member Directory" in labels
    assert "Offers" not in labels
    assert "Logs" in labels
    assert labels.index("Logs") == labels.index("Dashboard") + 1


def test_hub_portal_nav_member_includes_logs() -> None:
    session = SimpleNamespace(declarant_type="member")
    labels = [label for label, _, _ in hub_portal_nav_for_session(session)]
    assert "Logs" in labels


def test_remap_active_page_for_declarant() -> None:
    assert remap_active_page_for_declarant("member_directory", "member") == "offers"
    assert remap_active_page_for_declarant("offers", "supplier") == "member_directory"
    assert remap_active_page_for_declarant("hub_dashboard", "supplier") == "hub_dashboard"
