"""Unit tests for widgets.user_dropdown."""

from __future__ import annotations

from auth.session import UserSession
from widgets.user_dropdown import _PREFIX, _user_email, build_user_dropdown_html


def test_user_email_from_partner_key() -> None:
    session = UserSession(
        role_type="partner",
        partner_key="MEYLE",
        declarant_type="supplier",
        display_name="Meyle",
    )
    assert _user_email(session) == "meyle@nexus.com"


def test_build_user_dropdown_html_escapes_display_name() -> None:
    session = UserSession(
        role_type="partner",
        partner_key="X",
        declarant_type="supplier",
        display_name='<script>alert("x")</script>',
    )
    html = build_user_dropdown_html(session)
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert f'class="{_PREFIX}"' in html
    assert "Log out" in html
