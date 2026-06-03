"""Hub portal placeholder pages — reuse shared shell later."""

from __future__ import annotations

import streamlit as st

from auth.session import get_session
from theme.components import render_empty_state, render_page_header


def _placeholder(title: str, message: str) -> None:
    session = get_session()
    render_page_header(session.display_name)
    render_empty_state(title, message)


def render_member_directory(active_page: str = "member_directory") -> None:
    _placeholder("Member Directory", "Browse the Nexus member network. Full directory coming soon.")


def render_my_company(active_page: str = "my_company") -> None:
    _placeholder("My Company", "Manage your company profile and settings.")


def render_about(active_page: str = "about") -> None:
    _placeholder("About", "Learn about Nexus Automotive International.")


def render_services(active_page: str = "services") -> None:
    _placeholder("Services", "Explore Nexus services and programmes.")


def render_news(active_page: str = "news") -> None:
    _placeholder("News & Insights", "Latest news and industry insights.")


def render_help(active_page: str = "help") -> None:
    _placeholder("Help & Support Center", "Get help and contact support.")
